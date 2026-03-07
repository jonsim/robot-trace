#
# A standalone application that somewhat emulates rebot, consuming an output.xml
# file and emitting RobotTrace style trace output. Ideally this matches 1:1 with
# the trace that would have been produced 'live' via robot-trace.
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
import argparse
from datetime import datetime

from robot.api import ExecutionResult, ResultVisitor
from robot.model.control import (
    Break,
    Continue,
    Error,
    For,
    ForIteration,
    Group,
    If,
    IfBranch,
    Return,
    Try,
    TryBranch,
    Var,
    While,
    WhileIteration,
)
from robot.model.keyword import Keyword

from robot_trace.RobotTrace import (
    BufferedTracePrinter,
    RobotTraceArgs,
    TestStatistics,
    TestTimings,
    Verbosity,
)


class ResultVisitorListenerAdapter(ResultVisitor):
    """Adapter to convert Robot's ResultVisitor interface to the Listener API"""

    def __init__(self, listener):
        self.listener = listener

    def start_suite(self, suite):
        name = suite.name
        attributes = {
            "longname": suite.full_name,
            "totaltests": suite.test_count,
            "starttime": suite.start_time,
        }
        self.listener.start_suite(name, attributes)

    def end_suite(self, suite):
        name = suite.name
        attributes = {
            "longname": suite.full_name,
            "totaltests": suite.test_count,
            "status": suite.status,
            "message": suite.message,
            "elapsedtime": suite.elapsedtime,
            "endtime": suite.end_time,
        }
        self.listener.end_suite(name, attributes)

    def start_test(self, test):
        name = test.name
        attributes = {
            "longname": test.full_name,
            "starttime": test.start_time,
        }
        self.listener.start_test(name, attributes)

    def end_test(self, test):
        # If the test passed, but the suite teardown failed, the ResultVisitor
        # will report the test as failed. This is in contrast to the Listner API
        # which will report the test as passed, but then report an error after
        # end_test and before end_suite (which makes sense).
        # Fudge this behaviour on the ResultVisitor side, looking for the sole
        # failure being about the parent suite teardown failure, and report the
        # test as passed. The suite will still have status = FAIL, so this
        # achieves the desired behaviour.
        if test.message.startswith("Parent suite teardown failed:"):
            status = "PASS"
        else:
            status = test.status
        name = test.name
        attributes = {
            "longname": test.full_name,
            "status": status,
            "message": test.message,
            "elapsedtime": test.elapsedtime,
            "endtime": test.end_time,
        }
        self.listener.end_test(name, attributes)

    def start_message(self, message):
        self.listener.log_message(message)

    def visit_errors(self, errors):
        # Don't visit ResultVisitor.visit_errors - we see them as we
        # traverse the body items.
        pass

    def end_result(self, result):
        elapsed_time = result.suite.elapsed_time.total_seconds()
        self.listener.end_result(elapsed_time)

    # ============================================================
    # GENERIC BODY ITEM ROUTING
    # ============================================================

    def _start_body_item(self, node):
        name, attrs = self._node_to_listener_keyword(node, is_end=False)
        self.listener.start_keyword(name, attrs)

    def _end_body_item(self, node):
        name, attrs = self._node_to_listener_keyword(node, is_end=True)
        self.listener.end_keyword(name, attrs)

    # ============================================================
    # KEYWORD
    # ============================================================

    def start_keyword(self, keyword):
        self._start_body_item(keyword)

    def end_keyword(self, keyword):
        self._end_body_item(keyword)

    # ============================================================
    # FOR
    # ============================================================

    def start_for(self, node):
        self._start_body_item(node)

    def end_for(self, node):
        self._end_body_item(node)

    def start_for_iteration(self, node):
        self._start_body_item(node)

    def end_for_iteration(self, node):
        self._end_body_item(node)

    # ============================================================
    # IF
    # ============================================================

    # Don't visit the outer 'IF' block - instead visit the branches. This gives
    # parity in reporting with the Listener API.
    def start_if(self, node):
        pass

    def end_if(self, node):
        pass

    def start_if_branch(self, node):
        self._start_body_item(node)

    def end_if_branch(self, node):
        self._end_body_item(node)

    # ============================================================
    # TRY
    # ============================================================

    # Don't visit the outer 'TRY' block - instead visit the branches. This gives
    # parity in reporting with the Listener API.
    def start_try(self, node):
        pass

    def end_try(self, node):
        pass

    def start_try_branch(self, node):
        self._start_body_item(node)

    def end_try_branch(self, node):
        self._end_body_item(node)

    # ============================================================
    # WHILE
    # ============================================================

    def start_while(self, node):
        self._start_body_item(node)

    def end_while(self, node):
        self._end_body_item(node)

    def start_while_iteration(self, node):
        self._start_body_item(node)

    def end_while_iteration(self, node):
        self._end_body_item(node)

    # ============================================================
    # GROUP
    # ============================================================

    def start_group(self, node):
        self._start_body_item(node)

    def end_group(self, node):
        self._end_body_item(node)

    # ============================================================
    # VAR
    # ============================================================

    def start_var(self, node):
        self._start_body_item(node)

    def end_var(self, node):
        self._end_body_item(node)

    # ============================================================
    # RETURN
    # ============================================================

    def start_return(self, node):
        self._start_body_item(node)

    def end_return(self, node):
        self._end_body_item(node)

    # ============================================================
    # CONTINUE
    # ============================================================

    def start_continue(self, node):
        self._start_body_item(node)

    def end_continue(self, node):
        self._end_body_item(node)

    # ============================================================
    # BREAK
    # ============================================================

    def start_break(self, node):
        self._start_body_item(node)

    def end_break(self, node):
        self._end_body_item(node)

    # ============================================================
    # ERROR
    # ============================================================

    def start_error(self, node):
        self._start_body_item(node)

    def end_error(self, node):
        self._end_body_item(node)

    # ============================================================
    # CORE CONVERSION LOGIC
    # ============================================================

    @staticmethod
    def _node_to_listener_keyword(node, is_end=False):
        """Convert a ResultVisitor model node into the (name, attributes) pair
        that the V2 Listener API ``start_keyword`` / ``end_keyword`` expects.

        The *is_end* flag controls time-sensitive attributes:
        - ``status``  →  ``'NOT SET'`` at start, actual status at end.
        - ``elapsedtime``  →  ``0`` at start, ``node.elapsedtime`` at end.
        """
        status = node.status if is_end else "NOT SET"
        elapsed = node.elapsedtime if is_end else 0

        # --- Keyword (KEYWORD / SETUP / TEARDOWN) -----------------------
        if isinstance(node, Keyword):
            name = node.full_name or ""
            attributes = {
                "type": node.type,
                "kwname": node.kwname if hasattr(node, "kwname") else (node.name or ""),
                "libname": node.owner or "",
                "doc": node.doc,
                "args": list(node.args),
                "assign": list(node.assign),
                "tags": list(node.tags),
                "status": status,
                "elapsedtime": elapsed,
            }
            return name, attributes

        # -- Shared base for every control structure --------------------
        def _base(node_type, kwname=""):
            return {
                "type": node_type,
                "kwname": kwname,
                "libname": "",
                "doc": "",
                "args": [],
                "assign": [],
                "tags": [],
                "status": status,
                "elapsedtime": elapsed,
            }

        # --- FOR --------------------------------------------------------
        if isinstance(node, For):
            name = (
                f"{'    '.join(node.assign)}    {node.flavor}    "
                f"{'    '.join(node.values)}"
            )
            attrs = _base("FOR", name)
            attrs["variables"] = list(node.assign)
            attrs["flavor"] = node.flavor or ""
            attrs["values"] = list(node.values)
            attrs["start"] = node.start or ""
            attrs["mode"] = node.mode or ""
            attrs["fill"] = node.fill or ""
            return name, attrs

        # --- FOR iteration ----------------------------------------------
        if isinstance(node, ForIteration):
            assign = node.assign  # dict-like: {var: value}
            name = ", ".join(f"{k} = {v}" for k, v in assign.items())
            attrs = _base("ITERATION", name)
            attrs["variables"] = dict(assign)
            return name, attrs

        # --- WHILE ------------------------------------------------------
        if isinstance(node, While):
            name = node.condition or ""
            attrs = _base("WHILE", name)
            attrs["condition"] = node.condition or ""
            attrs["limit"] = node.limit or ""
            attrs["on_limit"] = node.on_limit or ""
            attrs["on_limit_message"] = node.on_limit_message or ""
            return name, attrs

        # --- WHILE iteration --------------------------------------------
        if isinstance(node, WhileIteration):
            name = ""
            attrs = _base("ITERATION", name)
            return name, attrs

        # --- GROUP ------------------------------------------------------
        if isinstance(node, Group):
            name = node.name or ""
            attrs = _base("GROUP", name)
            return name, attrs

        # --- IF (root container) ----------------------------------------
        if isinstance(node, If):
            name = ""
            attrs = _base("IF", name)
            return name, attrs

        # --- IF / ELSE IF / ELSE branch ---------------------------------
        if isinstance(node, IfBranch):
            name = node.condition or ""
            attrs = _base(node.type, name)
            attrs["condition"] = node.condition or ""
            return name, attrs

        # --- TRY (root container) ---------------------------------------
        if isinstance(node, Try):
            name = ""
            attrs = _base("TRY", name)
            return name, attrs

        # --- TRY / EXCEPT / ELSE / FINALLY branch -----------------------
        if isinstance(node, TryBranch):
            name = ""
            attrs = _base(node.type, name)
            attrs["patterns"] = list(node.patterns) if node.patterns else []
            attrs["pattern_type"] = node.pattern_type or ""
            attrs["variable"] = node.assign or ""
            return name, attrs

        # --- VAR --------------------------------------------------------
        if isinstance(node, Var):
            name = node.name + "    " + "    ".join(node.value)
            attrs = _base("VAR", name)
            attrs["name"] = node.name
            attrs["value"] = node.value or ""
            attrs["scope"] = node.scope or ""
            return name, attrs

        # --- RETURN -----------------------------------------------------
        if isinstance(node, Return):
            name = ""
            attrs = _base("RETURN", name)
            attrs["values"] = list(node.values) if node.values else []
            return name, attrs

        # --- CONTINUE ---------------------------------------------------
        if isinstance(node, Continue):
            name = ""
            attrs = _base("CONTINUE", name)
            return name, attrs

        # --- BREAK ------------------------------------------------------
        if isinstance(node, Break):
            name = ""
            attrs = _base("BREAK", name)
            return name, attrs

        # --- ERROR ------------------------------------------------------
        if isinstance(node, Error):
            name = ""
            attrs = _base("ERROR", name)
            attrs["values"] = list(node.values) if node.values else []
            return name, attrs

        # --- Fallback for unknown types ---------------------------------
        name = getattr(node, "full_name", "") or ""
        attrs = _base(getattr(node, "type", "KEYWORD"), name)
        return name, attrs


class ResultTestTimings(TestTimings):
    def _record_run_start(self, starttime: datetime):
        if self.run_start_time is None:
            self.run_start_time = starttime.timestamp()

    def start_suite(self, starttime: datetime):
        self._record_run_start(starttime)

    def end_suite(self, endtime: datetime):
        pass

    def start_test(self, starttime: datetime):
        self._record_run_start(starttime)
        self.current_test_start_time = starttime.timestamp()

    def end_test(self, endtime: datetime):
        self.current_test_start_time = None


class RebotTrace:
    def __init__(self, args: RobotTraceArgs):
        self.args = args
        self.stats = TestStatistics()
        self.timings = ResultTestTimings()
        self.result_printer = BufferedTracePrinter(
            print_passed=args.print_passed,
            print_skipped=args.print_skipped,
            print_warned=args.print_warned,
            print_errored=args.print_errored,
            print_failed=args.print_failed,
            colors=args.colors,
            width=args.width,
            print_callback=print,
        )
        self.in_test = False

    def start_suite(self, name, attributes):
        self.stats.start_suite(name, attributes)
        if "starttime" in attributes:
            self.timings.start_suite(attributes["starttime"])
        self.result_printer.start_suite(name, attributes)

    def end_suite(self, name, attributes):
        self.stats.end_suite(name, attributes)
        if "endtime" in attributes:
            self.timings.end_suite(attributes["endtime"])
        self.result_printer.end_suite(name, attributes)

    def start_test(self, name, attributes):
        self.in_test = True
        self.stats.start_test(name, attributes)
        if "starttime" in attributes:
            self.timings.start_test(attributes["starttime"])
        self.result_printer.start_test(name, attributes)

    def end_test(self, name, attributes):
        self.in_test = False
        self.stats.end_test(name, attributes)
        if "endtime" in attributes:
            self.timings.end_test(attributes["endtime"])
        self.result_printer.end_test(name, attributes)

    def start_keyword(self, name, attributes):
        self.result_printer.start_keyword(self.in_test, name, attributes)

    def end_keyword(self, name, attributes):
        self.result_printer.end_keyword(self.in_test, name, attributes)

    def log_message(self, message):
        attributes = {
            "level": message.level,
            "message": message.message,
        }
        self.result_printer.log_message(self.in_test, attributes)
        if message.level == "ERROR":
            self.stats.log_error(message.message)
        elif message.level == "WARN":
            self.stats.log_warning(message.message)

    def end_result(self, elapsed_time):
        if self.args.verbosity >= Verbosity.QUIET:
            print("RUN COMPLETE: " + self.stats.format_run_summary())
        if self.args.verbosity >= Verbosity.NORMAL:
            run_results = self.stats.format_run_results()
            if run_results:
                print("\n" + run_results)

        if (
            self.timings.run_start_time is not None
            and self.args.verbosity >= Verbosity.NORMAL
        ):
            elapsed_str = self.timings.format_time(elapsed_time)
            print(f"Total elapsed: {elapsed_str}.")


def main():
    parser = argparse.ArgumentParser(
        description="Example CLI with quiet/verbose flags and output file."
    )

    # Mutually exclusive verbosity flags
    verbosity_group = parser.add_mutually_exclusive_group()
    verbosity_group.add_argument(
        "--quiet", action="store_true", help="Suppress non-error output."
    )
    verbosity_group.add_argument(
        "--verbose", action="store_true", help="Enable detailed output."
    )
    parser.add_argument("output", help="Output XML file (e.g., output.xml).")
    args = parser.parse_args()

    # Parse arguments.
    if args.quiet:
        verbosity = "QUIET"
    elif args.verbose:
        verbosity = "DEBUG"
    else:
        verbosity = "NORMAL"
    robot_trace_args = RobotTraceArgs(
        verbosity=verbosity,
        colors="AUTO",
        console_progress="OFF",
        trace_subprocesses=False,
        can_stream_output=False,
    )

    result = ExecutionResult(args.output)
    listener = RebotTrace(robot_trace_args)
    result.visit(ResultVisitorListenerAdapter(listener))


if __name__ == "__main__":
    main()
