#
# A Robot listener to be invoked on all pabot sub-processes. This connects back
# to a top-level collector (PabotTraceCollector) and reports formatted results
# to it.
#
# This file is provided under the MIT license:
#
# MIT License
#
# Copyright (c) 2026 Jonathan Simmonds
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
import os
from xmlrpc.client import Binary, ServerProxy

from robot_trace.RobotTrace import RobotTrace, RobotTraceArgs

HOST = "127.0.0.1"


class PabotTraceReporter(RobotTrace):
    """
    A Robot Framework listener for pabot sub-processes that reports results back
    to a central PabotTraceCollector.
    """

    ROBOT_LISTENER_API_VERSION = 2

    def __init__(
        self,
        verbosity: str = RobotTraceArgs.DEFAULT_VERBOSITY,
        colors: str = RobotTraceArgs.DEFAULT_COLORS,
        trace_subprocesses: bool = RobotTraceArgs.DEFAULT_TRACE_SUBPROCESSES,
        width: int = RobotTraceArgs.DEFAULT_WIDTH,
    ):
        """
        Initialize the reporter and connect to the collector server.
        """
        super().__init__(
            verbosity=verbosity,
            colors=colors,
            console_progress="OFF",  # Never show progress from a reporter.
            trace_subprocesses=trace_subprocesses,
            width=width,
            can_stream_output=False,  # Never stream output from a reporter.
        )
        # Connect to the collector server
        port = int(os.environ["_PABOT_TRACE_COLLECTOR_PORT"])
        self.proxy = ServerProxy(f"http://{HOST}:{port}/", allow_none=True)
        self._uid = None
        self._queue_index = None
        self._pool_id = None
        self._process_count = None

    def _print_trace(self, text: str):
        """
        Send a formatted trace message to the collector server.
        """
        self.proxy.print_trace(
            self._uid, self._pool_id, self._queue_index, Binary(text.encode("utf-8"))
        )

    def _record_id(self):
        """
        Identify the pabot executor's ID and notify the collector.
        """
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
        """
        Notify the collector when a test suite starts.
        """
        if not self._uid:
            self._record_id()
        self.proxy.start_suite(
            self._uid, self._pool_id, self._queue_index, name, attributes
        )
        super().start_suite(name, attributes)

    def end_suite(self, name, attributes):
        """
        Notify the collector when a test suite ends.
        """
        self.proxy.end_suite(
            self._uid, self._pool_id, self._queue_index, name, attributes
        )
        super().end_suite(name, attributes)

    def start_test(self, name, attributes):
        """
        Notify the collector when a test case starts.
        """
        self.proxy.start_test(
            self._uid, self._pool_id, self._queue_index, name, attributes
        )
        super().start_test(name, attributes)

    def end_test(self, name, attributes):
        """
        Notify the collector when a test case ends.
        """
        self.proxy.end_test(
            self._uid, self._pool_id, self._queue_index, name, attributes
        )
        super().end_test(name, attributes)

    def log_message(self, attributes):
        """
        Notify the collector about log messages, ensuring errors and warnings are
        correctly categorized.
        """
        level = attributes["level"]
        text = attributes["message"]

        if level == "ERROR":
            self.proxy.log_error(self._uid, self._pool_id, self._queue_index, text)
        elif level == "WARN":
            self.proxy.log_warning(self._uid, self._pool_id, self._queue_index, text)

        super().log_message(attributes)
