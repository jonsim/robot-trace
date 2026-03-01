from xmlrpc.client import Binary, ServerProxy

from robot_trace.RobotTrace import RobotTrace, RobotTraceArgs

HOST = "127.0.0.1"
PORT = 5292


class PabotTraceReporter(RobotTrace):
    ROBOT_LISTENER_API_VERSION = 2

    def __init__(
        self,
        verbosity: str = RobotTraceArgs.DEFAULT_VERBOSITY,
        colors: str = RobotTraceArgs.DEFAULT_COLORS,
        trace_subprocesses: bool = RobotTraceArgs.DEFAULT_TRACE_SUBPROCESSES,
        width: int = RobotTraceArgs.DEFAULT_WIDTH,
    ):
        super().__init__(
            verbosity=verbosity,
            colors=colors,
            console_progress="OFF",  # Never show progress from a reporter.
            trace_subprocesses=trace_subprocesses,
            width=width,
            can_stream_output=False,  # Never stream output from a reporter.
        )
        # Connect to the collector server
        self.proxy = ServerProxy(f"http://{HOST}:{PORT}/", allow_none=True)
        self._uid = None
        self._queue_index = None
        self._pool_id = None
        self._process_count = None

    def _print_trace(self, text: str):
        self.proxy.print_trace(
            self._uid, self._pool_id, self._queue_index, Binary(text.encode("utf-8"))
        )

    def _record_id(self):
        from robot.libraries.BuiltIn import BuiltIn

        builtin = BuiltIn()
        self._uid = builtin.get_variable_value(r"${CALLER_ID}")
        self._queue_index = int(builtin.get_variable_value(r"${PABOTQUEUEINDEX}"))
        self._pool_id = int(builtin.get_variable_value(r"${PABOTEXECUTIONPOOLID}"))
        self._process_count = int(
            builtin.get_variable_value(r"${PABOTNUMBEROFPROCESSES}")
        )
        context = {
            "uid": self._uid,
            "queue_index": self._queue_index,
            "pool_id": self._pool_id,
            "process_count": self._process_count,
        }
        self.proxy.report_context(context)

    def start_suite(self, name, attributes):
        if not self._uid:
            self._record_id()
        self.proxy.start_suite(
            self._uid, self._pool_id, self._queue_index, name, attributes
        )
        super().start_suite(name, attributes)

    def end_suite(self, name, attributes):
        self.proxy.end_suite(
            self._uid, self._pool_id, self._queue_index, name, attributes
        )
        super().end_suite(name, attributes)

    def start_test(self, name, attributes):
        self.proxy.start_test(
            self._uid, self._pool_id, self._queue_index, name, attributes
        )
        super().start_test(name, attributes)

    def end_test(self, name, attributes):
        self.proxy.end_test(
            self._uid, self._pool_id, self._queue_index, name, attributes
        )
        super().end_test(name, attributes)

    def log_message(self, attributes):
        level = attributes["level"]
        text = attributes["message"]

        if level == "ERROR":
            self.proxy.log_error(self._uid, self._pool_id, self._queue_index, text)
        elif level == "WARN":
            self.proxy.log_warning(self._uid, self._pool_id, self._queue_index, text)

        super().log_message(attributes)
