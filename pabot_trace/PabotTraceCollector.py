#
# A wrapper around pabot that starts a collector server and invokes all robot
# sub-processes with a custom listener to report back to the collector. This
# file is provided under the MIT license.
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
import threading
import time
from socketserver import ThreadingMixIn
from xmlrpc.server import SimpleXMLRPCServer

from robot_trace.RobotTrace import (
    ANSI,
    ProgressBox,
    TestStatistics,
    TestTimings,
    Verbosity,
)

HOST = "127.0.0.1"
PORT = 0


class ThreadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass


class ThreadedTestStatistics(TestStatistics):
    def __init__(self):
        self.top_level_test_count = None
        self._stats: dict[str, TestStatistics] = {}

    def _get_suite_statistics(self, uid) -> TestStatistics:
        if uid not in self._stats:
            self._stats[uid] = TestStatistics()
        return self._stats[uid]

    @property
    def started_suites(self) -> list[str]:
        return [
            suite for stats in self._stats.values() for suite in stats.started_suites
        ]

    @property
    def started_tests(self) -> list[str]:
        return [test for stats in self._stats.values() for test in stats.started_tests]

    @property
    def passed_tests(self) -> list[str]:
        return [test for stats in self._stats.values() for test in stats.passed_tests]

    @property
    def skipped_tests(self) -> list[str]:
        return [test for stats in self._stats.values() for test in stats.skipped_tests]

    @property
    def failed_tests(self) -> list[str]:
        return [test for stats in self._stats.values() for test in stats.failed_tests]

    @property
    def completed_tests(self) -> list[str]:
        return [
            test for stats in self._stats.values() for test in stats.completed_tests
        ]

    @property
    def completed_suites(self) -> list[str]:
        return [
            suite for stats in self._stats.values() for suite in stats.completed_suites
        ]

    @property
    def warnings(self) -> dict[str, list[str]]:
        warnings = {}
        for stats in self._stats.values():
            warnings.update(stats.warnings)
        return warnings

    @property
    def errors(self) -> dict[str, list[str]]:
        errors = {}
        for stats in self._stats.values():
            errors.update(stats.errors)
        return errors

    def start_suite(self, uid, name, attributes):
        self._get_suite_statistics(uid).start_suite(name, attributes)

    def end_suite(self, uid, name, attributes):
        self._get_suite_statistics(uid).end_suite(name, attributes)

    def start_test(self, uid, name, attributes):
        self._get_suite_statistics(uid).start_test(name, attributes)

    def end_test(self, uid, name, attributes):
        self._get_suite_statistics(uid).end_test(name, attributes)

    def log_warning(self, uid, message):
        self._get_suite_statistics(uid).log_warning(message)

    def log_error(self, uid, message):
        self._get_suite_statistics(uid).log_error(message)


class ExecutorProgressBox(ProgressBox):
    def __init__(self, stream, colors: bool, width: int = 120):
        super().__init__(stream, 0, colors, width)
        self._executor_statuses: list[str] = []
        left_width = (self.width - 3) // 2
        right_width = self.width - 3 - left_width
        self._top_border = "┌" + "─" * left_width + "┬" + "─" * right_width + "┐"
        self._bottom_border = "└" + "─" * left_width + "┴" + "─" * right_width + "┘"
        self._blank_line = " " * (left_width - 1) + "│" + " " * (right_width - 1)

    def write_executor_status(self, executor_no: int, status: str = ""):
        if not self.stream:
            return
        # If we haven't seen this executor before, extend the list to the
        # required size.
        if executor_no >= len(self._executor_statuses):
            old_height = self._line_count + 2
            self._executor_statuses.extend(
                ["" for _ in range(executor_no - len(self._executor_statuses) + 1)]
            )
            # Correspondingly increase the number of status lines.
            required_lines = (executor_no // 2) + 1
            if required_lines > len(self._lines):
                self._lines.extend(
                    [self._blank_line for _ in range(required_lines - len(self._lines))]
                )
                self._line_count = len(self._lines)
                # Redraw
                self.stream.write(ANSI.Cursor.UP(old_height - 1) + ANSI.Cursor.HOME)
                self.draw()
        self._executor_statuses[executor_no] = status
        # Update the correct status line
        status_lineno = executor_no // 2
        side_width = (self.width - 7) // 2
        if executor_no % 2 == 0:
            left_executor = executor_no
            right_executor = executor_no + 1
        else:
            left_executor = executor_no - 1
            right_executor = executor_no
        left = self._executor_statuses[left_executor]
        right = (
            self._executor_statuses[right_executor]
            if right_executor < len(self._executor_statuses)
            else ""
        )
        status_text = (
            f"{left:<{side_width}.{side_width}} │ {right:<{side_width}.{side_width}}"
        )
        self.write_line(status_lineno, status_text)


class StreamedTracePrinter:
    def __init__(
        self,
        progress_box: ExecutorProgressBox,
        stats: ThreadedTestStatistics,
        print_callback,
    ):
        self.console_lock = threading.Lock()
        self.progress_box = progress_box
        self.stats = stats
        self.print = print_callback

    def _format_executor_id(self, pool_id: int, queue_id: int) -> str:
        executor_count = len(self.progress_box._executor_statuses)
        if executor_count < 10:
            return f"[{pool_id:1}][{queue_id:2}]"
        elif executor_count < 100:
            return f"[{pool_id:2}][{queue_id:2}]"
        else:
            return f"[{pool_id:3}][{queue_id:3}]"

    def report_test_count(self, test_count):
        self.stats.top_level_test_count = test_count
        self.progress_box.total_tasks = test_count

    def report_context(self, context):
        pass

    def start_suite(self, uid, pool_id, queue_id, name, attributes):
        self.stats.start_suite(uid, name, attributes)
        # self.timings.start_suite()
        executor_id = self._format_executor_id(pool_id, queue_id)
        with self.console_lock:
            self.progress_box.write_executor_status(
                pool_id, f"{executor_id}[SUITE] {name}"
            )

    def end_suite(self, uid, pool_id, queue_id, name, attributes):
        self.stats.end_suite(uid, name, attributes)
        executor_id = self._format_executor_id(pool_id, queue_id)
        with self.console_lock:
            self.progress_box.write_executor_status(pool_id, f"{executor_id}")

    def start_test(self, uid, pool_id, queue_id, name, attributes):
        self.stats.start_test(uid, name, attributes)
        executor_id = self._format_executor_id(pool_id, queue_id)
        with self.console_lock:
            self.progress_box.write_executor_status(
                pool_id, f"{executor_id}[TEST] {name}"
            )

    def end_test(self, uid, pool_id, queue_id, name, attributes):
        self.stats.end_test(uid, name, attributes)
        executor_id = self._format_executor_id(pool_id, queue_id)
        with self.console_lock:
            self.progress_box.add_task_status(attributes["status"])
            self.progress_box.write_executor_status(pool_id, f"{executor_id}")

    def log_warning(self, uid, pool_id, queue_id, message):
        self.stats.log_warning(uid, message)

    def log_error(self, uid, pool_id, queue_id, message):
        self.stats.log_error(uid, message)

    def print_trace(self, uid, pool_id, queue_id, binary_payload):
        text = binary_payload.data.decode("utf-8")
        with self.console_lock:
            self.print(text)


class PabotTraceCollector:
    def __init__(self, stream, progress_box: ProgressBox):
        self.stream = stream
        self.progress_box = progress_box
        self.verbosity = Verbosity.NORMAL
        self.stats = ThreadedTestStatistics()
        self.print_summary = True
        self.run_start_time = None
        self.server: ThreadedXMLRPCServer = None
        self.server_thread: threading.Thread = None
        self.port: int = 0

        # Finally, prepare the console interface.
        self.progress_box.draw()

    def _writeln(self, text=""):
        self.stream.write(text + "\n")
        self.stream.flush()

    def _print_trace(self, text: str):
        # First clear the progress box, so we don't have to worry about
        # interleaving with the trace output.
        self.progress_box.clear()
        # Then print the trace text as normal.
        self._writeln(text)
        # Finally redraw the progress box with the current test progress.
        self.progress_box.draw()

    def __enter__(self):
        self.run_start_time = time.time()
        # Create the trace writer.
        trace_writer = StreamedTracePrinter(
            self.progress_box, self.stats, self._print_trace
        )
        # Start the collector server.
        self.server = ThreadedXMLRPCServer(
            (HOST, PORT), allow_none=True, logRequests=False
        )
        self.port = int(self.server.server_address[1])
        self.server.register_function(
            trace_writer.report_test_count, "report_test_count"
        )
        self.server.register_function(trace_writer.report_context, "report_context")
        self.server.register_function(trace_writer.start_suite, "start_suite")
        self.server.register_function(trace_writer.end_suite, "end_suite")
        self.server.register_function(trace_writer.start_test, "start_test")
        self.server.register_function(trace_writer.end_test, "end_test")
        self.server.register_function(trace_writer.log_warning, "log_warning")
        self.server.register_function(trace_writer.log_error, "log_error")
        self.server.register_function(trace_writer.print_trace, "print_trace")
        # Run server in a background thread.
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # First, shutdown the server.
        self.server.shutdown()
        self.server.server_close()
        self.server_thread.join()

        # Then clear the progress box.
        self.progress_box.clear()

        # And finally print a summary of the run.
        if self.print_summary:
            if self.verbosity >= Verbosity.QUIET:
                self._writeln("RUN COMPLETE: " + self.stats.format_run_summary())
            if self.verbosity >= Verbosity.NORMAL:
                run_results = self.stats.format_run_results()
                if run_results:
                    self._writeln("\n" + run_results)
            if self.run_start_time is not None and self.verbosity >= Verbosity.NORMAL:
                elapsed_str = TestTimings.format_time(time.time() - self.run_start_time)
                self._writeln(f"Total elapsed: {elapsed_str}.")
