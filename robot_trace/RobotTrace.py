#
# Prints Robot test progress to stdout as execution happens. Refer to the README
# for usage instructions. This file is provided under the MIT license.
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
import enum
import functools
import re
import shutil
import sys
import time
from collections.abc import Iterable
from typing import Literal


@functools.total_ordering
class Verbosity(enum.Enum):
    QUIET = 0
    NORMAL = 1
    DEBUG = 2

    def __eq__(self, value):
        if isinstance(value, Verbosity):
            return self.value == value.value
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, Verbosity):
            return self.value < other.value
        return NotImplemented

    @classmethod
    def from_string(cls, s):
        s = s.upper()
        if s in cls.__members__:
            return cls[s]
        return cls.NORMAL


# ANSI escape codes for colors and styles.
class _ANSICode:
    def __init__(self, code: str):
        self.code = code

    def __call__(self, text: str) -> str:
        return f"{self.code}{text}{ANSI.RESET}"

    def __repr__(self) -> str:
        return self.code

    def __str__(self) -> str:
        return self.code


class ANSI:
    RESET = _ANSICode("\033[0m")

    class Cursor:
        CLEAR_LINE = "\033[2K"

        HOME = "\r"

        @staticmethod
        def UP(n: int = 1) -> str:
            return f"\033[{n}A"

        @staticmethod
        def DOWN(n: int = 1) -> str:
            return f"\033[{n}B"

        @staticmethod
        def LEFT(n: int = 1) -> str:
            return f"\033[{n}D"

        @staticmethod
        def RIGHT(n: int = 1) -> str:
            return f"\033[{n}C"

    class Fore:
        BLACK = _ANSICode("\033[30m")
        RED = _ANSICode("\033[31m")
        GREEN = _ANSICode("\033[32m")
        YELLOW = _ANSICode("\033[33m")
        BLUE = _ANSICode("\033[34m")
        MAGENTA = _ANSICode("\033[35m")
        CYAN = _ANSICode("\033[36m")
        WHITE = _ANSICode("\033[37m")
        BRIGHT_BLACK = _ANSICode("\033[90m")
        BRIGHT_RED = _ANSICode("\033[91m")
        BRIGHT_GREEN = _ANSICode("\033[92m")
        BRIGHT_YELLOW = _ANSICode("\033[93m")
        BRIGHT_BLUE = _ANSICode("\033[94m")
        BRIGHT_MAGENTA = _ANSICode("\033[95m")
        BRIGHT_CYAN = _ANSICode("\033[96m")
        BRIGHT_WHITE = _ANSICode("\033[97m")

    class Back:
        BLACK = _ANSICode("\033[40m")
        RED = _ANSICode("\033[41m")
        GREEN = _ANSICode("\033[42m")
        YELLOW = _ANSICode("\033[43m")
        BLUE = _ANSICode("\033[44m")
        MAGENTA = _ANSICode("\033[45m")
        CYAN = _ANSICode("\033[46m")
        WHITE = _ANSICode("\033[47m")
        BRIGHT_BLACK = _ANSICode("\033[100m")
        BRIGHT_RED = _ANSICode("\033[101m")
        BRIGHT_GREEN = _ANSICode("\033[102m")
        BRIGHT_YELLOW = _ANSICode("\033[103m")
        BRIGHT_BLUE = _ANSICode("\033[104m")
        BRIGHT_MAGENTA = _ANSICode("\033[105m")
        BRIGHT_CYAN = _ANSICode("\033[106m")
        BRIGHT_WHITE = _ANSICode("\033[107m")

    class Style:
        BOLD = _ANSICode("\033[1m")
        DIM = _ANSICode("\033[2m")
        ITALIC = _ANSICode("\033[3m")
        UNDERLINE = _ANSICode("\033[4m")
        BLINK = _ANSICode("\033[5m")
        INVERT = _ANSICode("\033[7m")
        HIDDEN = _ANSICode("\033[8m")

    @staticmethod
    def len(text: str) -> int:
        """Return the length of the text, ignoring ANSI escape codes."""
        return len(re.sub(r"\033\[[0-9;]*m", "", text))


class TraceStack:
    def __init__(self, name: str):
        self.name = name
        self._trace: str = ""
        self._depth: int = 0
        self._stack: list[str] = []
        self.has_warnings: bool = False
        self.has_errors: bool = False
        self.has_failures: bool = False

    def reset(self, name: str):
        self.name = name
        self._trace = ""
        self._depth = 0
        self._stack.clear()
        self.has_warnings = False
        self.has_errors = False
        self.has_failures = False

    @property
    def _indent(self) -> str:
        return "  " * min(self._depth, 20)

    @property
    def trace(self) -> str:
        return self._trace

    def push_keyword(self, keyword_line: str):
        self._stack.append(self._indent + keyword_line)
        self._depth += 1

    def pop_keyword(self):
        self._stack.pop()
        self._depth -= 1

    def append_trace(self, trace_lines: str):
        trace_lines = "\n".join(
            self._indent + line for line in trace_lines.splitlines()
        )
        self._trace += trace_lines + "\n"

    def flush(self, decrement_depth: bool = True):
        """Flush any pending keyword headers to the trace and clear the stack."""
        if decrement_depth:
            self._depth -= 1
        for trace_line in self._stack:
            self._trace += trace_line + "\n"
        self._stack.clear()


class TracePrinter:
    def __init__(
        self,
        print_passed: bool,
        print_skipped: bool,
        print_warned: bool,
        print_errored: bool,
        print_failed: bool,
        colors: bool,
        width: int,
        print_callback,
    ):
        self.print_passed = print_passed
        self.print_skipped = print_skipped
        self.print_warned = print_warned
        self.print_errored = print_errored
        self.print_failed = print_failed
        self.colors = colors
        self.width = width
        self.print = print_callback

    def log_message_to_console(
        self, in_test: bool, message: str, stream: Literal["stdout", "stderr"]
    ):
        self.print(f"Logged from test {stream}: {message.rstrip()}")

    def _format_banner(self, status_text: str, status_color, name: str) -> str:
        if self.colors and status_color:
            status_text = status_color(status_text)
        status_line = f"{status_text}: {name}"
        underline_length = min(self.width, ANSI.len(status_line))
        underline = "═" * underline_length
        return f"{status_line}\n{underline}"

    def _format_keyword_header(self, name: str, attributes: dict) -> str:
        kwtype = attributes["type"]
        args = attributes["args"]
        if kwtype != "KEYWORD":
            name = f"{kwtype}    {name}" if name else kwtype
        if args or kwtype in {"KEYWORD", "SETUP", "TEARDOWN"}:
            argstr = "(" + ", ".join(repr(a) for a in args) + ")"
        else:
            argstr = ""
        return f"▶ {name}{argstr}"

    def _format_keyword_status(self, status: str, elapsed_time_ms: int) -> str:
        elapsed = TestTimings.format_time(elapsed_time_ms / 1000)
        if status == "PASS":
            status_text = "✓ PASS"
            if self.colors:
                status_text = ANSI.Fore.BRIGHT_GREEN(status_text)
            return f"  {status_text}    {elapsed}"
        elif status == "SKIP":
            status_text = "→ SKIP"
            if self.colors:
                status_text = ANSI.Fore.YELLOW(status_text)
            return f"  {status_text}    {elapsed}"
        elif status == "FAIL":
            status_text = "✗ FAIL"
            if self.colors:
                status_text = ANSI.Fore.BRIGHT_RED(status_text)
            return f"  {status_text}    {elapsed}"
        elif status == "NOT RUN":
            status_text = "⊘ NOT RUN"
            if self.colors:
                status_text = ANSI.Fore.BRIGHT_BLACK(status_text)
            return f"  {status_text}    {elapsed}"
        else:
            return f"  ? {status}    {elapsed}"

    def _format_log_message(self, level: str, text: str, indent: str = "") -> list[str]:
        level_initial = level[0].upper()
        text_lines = text.splitlines()
        lines = []
        lines.append(f"{indent}{level_initial} {text_lines[0]}")
        for text_line in text_lines[1:]:
            lines.append(f"{indent}  {text_line}")

        if self.colors:
            if level == "ERROR" or level == "FAIL":
                lines = [ANSI.Fore.BRIGHT_RED(line) for line in lines]
            elif level == "WARN":
                lines = [ANSI.Fore.BRIGHT_YELLOW(line) for line in lines]
            elif level == "SKIP":
                lines = [ANSI.Fore.YELLOW(line) for line in lines]
            elif level == "INFO":
                lines = [ANSI.Fore.BRIGHT_BLACK(line) for line in lines]
            elif level == "DEBUG" or level == "TRACE":
                lines = [ANSI.Fore.WHITE(line) for line in lines]
        return lines


class BufferedTracePrinter(TracePrinter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.test_trace_stack = TraceStack("<prerun>")
        self.suite_trace_stack = TraceStack("<prerun>")

    def start_suite(self, name, attributes):
        suite_name = attributes["longname"]
        self.suite_trace_stack.reset(suite_name)

    def end_suite(self, name, attributes):
        trace = self.suite_trace_stack.trace

        status = attributes["status"]
        status_text = ""
        if trace:
            should_print = self.print_passed
            status_text = "SUITE " + _past_tense(status)
            status_color = None
            if self.suite_trace_stack.has_failures:
                should_print |= self.print_failed
                status_color = ANSI.Fore.RED
            if self.suite_trace_stack.has_errors:
                should_print |= self.print_errored
                status_text += " WITH ERRORS"
                status_color = ANSI.Fore.RED
            if self.suite_trace_stack.has_warnings:
                should_print |= self.print_warned
                status_text += " WITH WARNINGS"
                status_color = ANSI.Fore.BRIGHT_YELLOW
            if should_print:
                banner = self._format_banner(
                    status_text, status_color, attributes["longname"]
                )
                if not trace:
                    trace = attributes["message"] + "\n"
                self.print(f"{banner}\n{trace}")

    def start_test(self, name, attributes):
        test_name = attributes["longname"]
        self.test_trace_stack.reset(test_name)

    def end_test(self, name, attributes):
        trace = self.test_trace_stack.trace
        status = attributes["status"]
        if status != "NOT RUN":
            should_print = False
            status_text = "TEST " + _past_tense(status)
            status_color = None
            if status == "PASS":
                should_print = self.print_passed
                status_color = ANSI.Fore.GREEN
            elif status == "SKIP":
                should_print = self.print_skipped
                status_color = ANSI.Fore.YELLOW
            elif status == "FAIL":
                should_print = self.print_failed
                status_color = ANSI.Fore.RED
            if self.test_trace_stack.has_errors:
                should_print |= self.print_errored
                status_text += " WITH ERRORS"
                status_color = ANSI.Fore.RED
            if self.test_trace_stack.has_warnings:
                should_print |= self.print_warned
                status_text += " WITH WARNINGS"
                status_color = ANSI.Fore.BRIGHT_YELLOW
            if should_print:
                banner = self._format_banner(
                    status_text, status_color, attributes["longname"]
                )
                if not trace:
                    trace = attributes["message"] + "\n"
                self.print(f"{banner}\n{trace}")

    def start_keyword(self, in_test: bool, name, attributes):
        stack = self.test_trace_stack if in_test else self.suite_trace_stack
        trace_line = self._format_keyword_header(name, attributes)
        stack.push_keyword(trace_line)

    def end_keyword(self, in_test: bool, name, attributes):
        stack = self.test_trace_stack if in_test else self.suite_trace_stack
        status = attributes["status"]
        if status == "NOT RUN":
            # Discard; the header was never flushed so it just disappears.
            stack.pop_keyword()
            return

        # Keyword ran - flush any pending ancestor headers (and this one)
        # so the hierarchy appears in the trace.
        stack.flush()

        keyword_trace = self._format_keyword_status(status, attributes["elapsedtime"])
        stack.append_trace(keyword_trace)

    def log_message(self, in_test: bool, attributes):
        level = attributes["level"]
        text = attributes["message"]

        # Flush keyword headers so they appear above the log line.
        stack = self.test_trace_stack if in_test else self.suite_trace_stack
        stack.flush(decrement_depth=False)

        if level == "ERROR":
            stack.has_errors = True
        elif level == "WARN":
            stack.has_warnings = True
        elif level == "FAIL":
            stack.has_failures = True

        lines = self._format_log_message(level, text)
        stack.append_trace("\n".join(lines))


class LiveTracePrinter(TracePrinter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.indent = 0

    def start_suite(self, name, attributes):
        suite_name = attributes["longname"]
        banner = self._format_banner("SUITE", None, suite_name)
        self.print(banner)

    def end_suite(self, name, attributes):
        pass

    def start_test(self, name, attributes):
        test_name = attributes["longname"]
        banner = self._format_banner("TEST", None, test_name)
        self.print(banner)

    def end_test(self, name, attributes):
        self.print("")

    def start_keyword(self, in_test: bool, name, attributes):
        trace_line = self._format_keyword_header(name, attributes)
        self.print(" " * self.indent * 2 + trace_line)
        self.indent += 1

    def end_keyword(self, in_test: bool, name, attributes):
        self.indent -= 1

        status = attributes["status"]

        keyword_trace = self._format_keyword_status(status, attributes["elapsedtime"])
        self.print(" " * self.indent * 2 + keyword_trace)

    def log_message(self, in_test: bool, attributes):
        level = attributes["level"]
        text = attributes["message"]

        indent = " " * self.indent * 2
        lines = self._format_log_message(level, text, indent)
        self.print("\n".join(lines))


class TestStatistics:
    def __init__(self):
        self.top_level_test_count: int | None = None
        self.current_suite: str | None = None
        self.current_test: str | None = None
        self.started_suites = []
        self.started_tests = []
        self.passed_tests = []
        self.skipped_tests = []
        self.failed_tests = []
        self.completed_tests = []
        self.completed_suites = []
        self.warnings: dict[str, list[str]] = {}
        self.errors: dict[str, list[str]] = {}

    def start_suite(self, name, attributes):
        suite_name = attributes["longname"]
        self.current_suite = suite_name
        self.started_suites.append(suite_name)
        if self.top_level_test_count is None:
            self.top_level_test_count = attributes["totaltests"]

    def end_suite(self, name, attributes):
        suite_name = attributes["longname"]
        self.current_suite = None
        self.completed_suites.append(suite_name)

    def start_test(self, name, attributes):
        test_name = attributes["longname"]
        self.current_test = test_name
        self.started_tests.append(test_name)

    def end_test(self, name, attributes):
        status = attributes["status"]
        test_name = attributes["longname"]
        self.current_test = None
        if status == "NOT RUN":
            return
        self.completed_tests.append(test_name)
        if status == "PASS":
            self.passed_tests.append(test_name)
        elif status == "FAIL":
            self.failed_tests.append(test_name)
        elif status == "SKIP":
            self.skipped_tests.append(test_name)

    def log_error(self, text: str):
        self.errors.setdefault(
            self.current_test if self.current_test else self.current_suite, []
        ).append(text)

    def log_warning(self, text: str):
        self.warnings.setdefault(
            self.current_test if self.current_test else self.current_suite, []
        ).append(text)

    def format_suite_progress(self) -> str:
        return f"{len(self.started_suites):2d}"

    def format_test_progress(self) -> str:
        return f"{len(self.started_tests):2d}/{self.top_level_test_count:2d}"

    def format_run_summary(self) -> str:
        plural = "s" if self.top_level_test_count != 1 else ""
        summary = (
            f"{self.top_level_test_count or 0} test{plural}, "
            f"{len(self.completed_tests)} completed "
            f"({len(self.passed_tests)} passed, "
            f"{len(self.skipped_tests)} skipped, "
            f"{len(self.failed_tests)} failed)."
        )
        if self.errors:
            plural = "s" if len(self.errors) != 1 else ""
            summary += f" {len(self.errors)} test{plural} raised errors."
        if self.warnings:
            plural = "s" if len(self.warnings) != 1 else ""
            summary += f" {len(self.warnings)} test{plural} raised warnings."
        return summary

    def format_run_results(self) -> str:
        results = ""
        if self.failed_tests:
            plural = "s" if len(self.failed_tests) != 1 else ""
            results += f"Failing test{plural}:\n"
            for test in self.failed_tests:
                results += f"- {test}\n"
        if self.errors:
            plural = "s" if len(self.errors) != 1 else ""
            results += f"Erroring test{plural}:\n"
            for test, messages in self.errors.items():
                results += f"- {test}:\n"
                for message in messages:
                    results += f"  - {message}\n"
        if self.warnings:
            plural = "s" if len(self.warnings) != 1 else ""
            results += f"Warning test{plural}:\n"
            for test, messages in self.warnings.items():
                results += f"- {test}:\n"
                for message in messages:
                    results += f"  - {message}\n"
        return results


class TestTimings:
    def __init__(self):
        self.run_start_time: float | None = None
        self.current_test_start_time: float | None = None

    def _record_run_start(self):
        if self.run_start_time is None:
            self.run_start_time = time.time()

    def start_suite(self):
        self._record_run_start()

    def start_test(self):
        self._record_run_start()
        self.current_test_start_time = time.time()

    def end_test(self):
        self.current_test_start_time = None

    @staticmethod
    def format_time(seconds: float | int | None) -> str:
        if seconds is None:
            return "unknown"
        seconds = int(round(seconds))
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        if h:
            return f"{h:2d}h {m:2d}m {s:2d}s"
        elif m:
            return f"{m:2d}m {s:2d}s"
        else:
            return f"{s:2d}s"

    def get_elapsed_time(self) -> float:
        if self.run_start_time is None:
            return 0.0
        return time.time() - self.run_start_time

    def format_elapsed_time(self) -> str:
        return self.format_time(self.get_elapsed_time())

    def format_eta(self, stats: TestStatistics) -> str:
        if stats.top_level_test_count and stats.completed_tests:
            elapsed_time = self.get_elapsed_time()
            avg_test_time = elapsed_time / len(stats.completed_tests)
            remaining_tests = stats.top_level_test_count - len(stats.completed_tests)
            eta_time = avg_test_time * remaining_tests
            return self.format_time(eta_time)
        return "unknown"


class ProgressBox:
    def __init__(self, stream, width: int = 120):
        self.stream = stream
        self.width = width
        self._lines = ["", "", ""]
        self._display_progress_bar = width >= 40
        self._total_tasks = None
        self._completed_tasks = 0

    def draw(self):
        if not self.stream:
            return

        if self._total_tasks is not None and self._display_progress_bar:
            # If we know the total number of tasks we will execute, draw the
            # progress bar at the top of the box.
            bar_length = self.width - 20
            completion = self._completed_tasks / self._total_tasks
            bar_completed = int(completion * bar_length)
            bar_remaining = bar_length - bar_completed
            self.stream.write(
                "┌"
                + "─" * 8
                + "┤"
                + "█" * bar_completed
                + "░" * bar_remaining
                + "├"
                + "─" * 8
                + "┐\n"
            )
        else:
            # Otherwise just draw a solid top border.
            self.stream.write("┌" + "─" * (self.width - 2) + "┐\n")

        # Write the three lines of text.
        text_width = self.width - 4
        for i in range(3):
            self.stream.write(f"│ {self._lines[i]:<{text_width}.{text_width}} │\n")

        # Write the bottom border.
        self.stream.write("└" + "─" * (self.width - 2) + "┘")
        self.stream.flush()

    @property
    def total_tasks(self) -> int | None:
        return self._total_tasks

    @total_tasks.setter
    def total_tasks(self, value: int):
        assert value > 0, "total_tasks must be positive"
        old_value = self._total_tasks
        self._total_tasks = value
        if old_value != value:
            self.clear()
            self.draw()

    @property
    def completed_tasks(self) -> int:
        return self._completed_tasks

    @completed_tasks.setter
    def completed_tasks(self, value: int):
        assert value >= 0, "completed_tasks must be non-negative"
        old_value = self._completed_tasks
        self._completed_tasks = value
        if old_value != value:
            self.clear()
            self.draw()

    def clear(self):
        if not self.stream:
            return
        # Clear the current line and move the cursor up. Do this 5 times to
        # clear the entire box (3 lines of text + top and bottom borders).
        for _ in range(4):
            self.stream.write(ANSI.Cursor.CLEAR_LINE + ANSI.Cursor.UP())
        # Clear the final line and reset the cursor to the start of the line.
        self.stream.write(ANSI.Cursor.CLEAR_LINE + ANSI.Cursor.HOME)
        self.stream.flush()

    def write_line(self, line_no: int, left_text: str = "", right_text: str = ""):
        if not self.stream:
            return
        # Format the left and right text into a single line. Right text takes
        # priority. Truncate left text with '...' if necessary.
        text_width = self.width - 4
        right_len = len(right_text)
        max_left = text_width - right_len - 1 if right_len > 0 else text_width
        max_left = max(0, max_left)
        if len(left_text) > max_left:
            if max_left >= 3:
                left_text = left_text[: max_left - 3] + "..."
            else:
                left_text = left_text[:max_left]
        padding = max(0, text_width - len(left_text) - right_len)
        text = f"{left_text}{' ' * padding}{right_text}"

        # Move cursor to the line inside the box and write the text.
        # For line 0, we want to move up 3 lines (to the first empty line in the box).
        # For line 1, we want to move up 2 lines.
        # For line 2, we want to move up 1 line.
        assert line_no >= 0 and line_no < 3, "line_no must be between 0 and 2"
        self._lines[line_no] = text
        line_offset = 3 - line_no
        self.stream.write(ANSI.Cursor.UP(line_offset))
        self.stream.write(ANSI.Cursor.HOME + f"│ {text} │")
        # Move cursor back down to the bottom of the box.
        self.stream.write(ANSI.Cursor.DOWN(line_offset))
        self.stream.flush()


class InterceptStream:
    def __init__(self, real_stream, write_callback):
        self._real_stream = real_stream
        self._write_callback = write_callback
        self.written_lines = []

    def write(self, msg: str) -> int:
        self.written_lines.append(msg)
        return len(msg)

    def writelines(self, lines: Iterable[str]) -> None:
        for line in lines:
            self.write(line)

    def flush(self):
        for line in self.written_lines:
            self._write_callback(line)
        self.written_lines.clear()

    # Forward everything else.
    def __getattr__(self, name):
        return getattr(self._real_stream, name)


class RobotTrace:
    ROBOT_LISTENER_API_VERSION = 2

    def __init__(
        self,
        verbosity: str = "NORMAL",
        colors: str = "AUTO",
        console_progress: str = "AUTO",
        width: int = 120,
    ):
        # Parse verbosity argument.
        verbosity = verbosity.upper()
        self.verbosity = Verbosity.from_string(verbosity)
        # Parse colors argument.
        colors = colors.upper()
        if colors in {"ON", "ANSI"}:
            self.colors = True
        elif colors in {"OFF"}:
            self.colors = False
        else:  # Assume AUTO.
            if sys.stdout.isatty():
                if sys.platform == "win32":
                    import importlib.util

                    self.colors = importlib.util.find_spec("colorama") is not None
                else:
                    self.colors = True
            else:
                self.colors = False
        # Parse console_progress argument.
        console_progress = console_progress.upper()
        if console_progress == "AUTO":
            if sys.stdout.isatty():
                progress_stream = sys.stdout
            elif sys.stderr.isatty():
                progress_stream = sys.stderr
            else:
                progress_stream = None
        elif console_progress == "STDOUT":
            progress_stream = sys.stdout
        elif console_progress == "STDERR":
            progress_stream = sys.stderr
        else:  # Assume NONE.
            progress_stream = None

        # Configure output based on verbosity.
        self.live_output = self.verbosity >= Verbosity.DEBUG
        self.print_passed = self.verbosity >= Verbosity.DEBUG
        self.print_skipped = self.verbosity >= Verbosity.DEBUG
        self.print_warned = self.verbosity >= Verbosity.NORMAL
        self.print_errored = self.verbosity >= Verbosity.NORMAL
        self.print_failed = self.verbosity >= Verbosity.QUIET

        # Set properties.
        self.terminal_width = min(
            shutil.get_terminal_size(fallback=(width, 40)).columns, width
        )
        self.progress_box = ProgressBox(progress_stream, self.terminal_width)
        self.stats = TestStatistics()
        self.timings = TestTimings()
        if self.live_output:
            self.result_printer = LiveTracePrinter(
                print_passed=self.print_passed,
                print_skipped=self.print_skipped,
                print_warned=self.print_warned,
                print_errored=self.print_errored,
                print_failed=self.print_failed,
                colors=self.colors,
                width=self.terminal_width,
                print_callback=self._print_trace,
            )
        else:
            self.result_printer = BufferedTracePrinter(
                print_passed=self.print_passed,
                print_skipped=self.print_skipped,
                print_warned=self.print_warned,
                print_errored=self.print_errored,
                print_failed=self.print_failed,
                colors=self.colors,
                width=self.terminal_width,
                print_callback=self._print_trace,
            )

        # On Windows, import colorama if we're coloring output.
        if self.colors and sys.platform == "win32":
            import colorama

            colorama.just_fix_windows_console()

        # Reconfigure the logging. Robot doesn't really support this very nicely
        # - it forces everything to sys.__stdout__ and sys.__stderr__ (not even
        # sys.stdout/sys.stderr), rather than going via a logger or other
        # configurable mechanism. There's no command line options to change
        # this.
        # Thus, install an interceptor to catch all output on both streams. The
        # intercepted output can then be integrated into the formatted output.
        self.real_stdout = sys.__stdout__
        self.real_stderr = sys.__stderr__
        self.intercepted_stdout = InterceptStream(
            self.real_stdout, lambda msg: self.log_message_to_console(msg, "stdout")
        )
        self.intercepted_stderr = InterceptStream(
            self.real_stderr, lambda msg: self.log_message_to_console(msg, "stderr")
        )
        sys.__stdout__ = self.intercepted_stdout
        sys.__stderr__ = self.intercepted_stderr

        # Finally, prepare the console interface.
        self.progress_box.draw()

    # ------------------------------------------------------------------ helpers

    @property
    def in_test(self) -> bool:
        return self.timings.current_test_start_time is not None

    def _writeln(self, text=""):
        self.real_stdout.write(text + "\n")
        self.real_stdout.flush()

    def _print_trace(self, text: str):
        # First clear the progress box, so we don't have to worry about
        # interleaving with the trace output.
        self.progress_box.clear()
        # Then print the trace text as normal.
        self._writeln(text)
        # Finally redraw the progress box with the current test progress.
        self.progress_box.draw()

    # ------------------------------------------------------------------ suite

    def start_suite(self, name, attributes):
        suite_name = attributes["longname"]
        self.stats.start_suite(name, attributes)
        if self.stats.top_level_test_count is not None:
            self.progress_box.total_tasks = self.stats.top_level_test_count
        self.timings.start_suite()
        self.result_printer.start_suite(name, attributes)

        self.progress_box.write_line(
            0, f"[SUITE {self.stats.format_suite_progress()}] {suite_name}"
        )

    def end_suite(self, name, attributes):
        self.stats.end_suite(name, attributes)
        self.result_printer.end_suite(name, attributes)

        self.progress_box.write_line(0)

    # ------------------------------------------------------------------ test

    def start_test(self, name, attributes):
        self.stats.start_test(name, attributes)
        self.timings.start_test()
        self.result_printer.start_test(name, attributes)

        self.progress_box.write_line(
            1,
            f"[TEST {self.stats.format_test_progress()}] {name}",
            f"(elapsed {self.timings.format_elapsed_time()}, "
            f"ETA {self.timings.format_eta(self.stats)})",
        )

    def end_test(self, name, attributes):
        self.stats.end_test(name, attributes)
        self.timings.end_test()
        self.progress_box.completed_tasks += 1
        self.progress_box.write_line(1)
        self.result_printer.end_test(name, attributes)

    # ------------------------------------------------------------------ keyword

    def start_keyword(self, name, attributes):
        self.result_printer.start_keyword(self.in_test, name, attributes)

        kwtype = attributes["type"]
        kwname = attributes["kwname"]
        args = attributes["args"]
        if kwtype != "KEYWORD":
            name = f"{kwtype}    {name}" if name else kwtype
        if args or kwtype in {"KEYWORD", "SETUP", "TEARDOWN"}:
            argstr = "(" + ", ".join(repr(a) for a in args) + ")"
        else:
            argstr = ""
        self.progress_box.write_line(2, f"[{kwname}]  {argstr}")

    def end_keyword(self, name, attributes):
        self.result_printer.end_keyword(self.in_test, name, attributes)

        self.progress_box.write_line(2)

    # ------------------------------------------------------------------ logging

    def log_message(self, attributes):
        self.result_printer.log_message(self.in_test, attributes)
        level = attributes["level"]
        text = attributes["message"]

        if level == "ERROR":
            self.stats.log_error(text)
        elif level == "WARN":
            self.stats.log_warning(text)

    def log_message_to_console(self, message: str, stream: Literal["stdout", "stderr"]):
        self.result_printer.log_message_to_console(self.in_test, message, stream)

    # ------------------------------------------------------------------ close

    def close(self):
        self.progress_box.clear()

        if self.verbosity >= Verbosity.QUIET:
            self._writeln("RUN COMPLETE: " + self.stats.format_run_summary())
        if self.verbosity >= Verbosity.NORMAL:
            run_results = self.stats.format_run_results()
            if run_results:
                self._writeln("\n" + run_results)

        if (
            self.timings.run_start_time is not None
            and self.verbosity >= Verbosity.NORMAL
        ):
            elapsed_str = self.timings.format_elapsed_time()
            self._writeln(f"Total elapsed: {elapsed_str}.")


def _past_tense(verb: str) -> str:
    is_upper = verb.isupper()
    is_title = verb.istitle()
    v = verb.lower()
    if v.endswith("e"):
        res = v + "d"
    elif v.endswith("y"):
        res = v[:-1] + "ied"
    elif v.endswith("p"):
        res = v + "ped"
    else:
        res = v + "ed"
    if is_upper:
        return res.upper()
    elif is_title:
        return res.title()
    return res
