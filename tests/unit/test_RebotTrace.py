# Unit tests for RebotTrace.py.
#
# Copyright (c) 2026 Jonathan Simmonds
import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

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

from rebot_trace.RebotTrace import (
    RebotTrace,
    ResultTestTimings,
    ResultVisitorListenerAdapter,
)
from robot_trace.RobotTrace import RobotTraceArgs, Verbosity


class TestResultTestTimings(unittest.TestCase):
    def test_start_suite_records_time(self):
        timings = ResultTestTimings()
        dt = datetime(2023, 1, 1, 12, 0, 0)
        timings.start_suite(dt)
        self.assertEqual(timings.run_start_time, dt.timestamp())

    def test_start_test_records_run_time_if_not_set(self):
        timings = ResultTestTimings()
        dt = datetime(2023, 1, 1, 12, 0, 0)
        timings.start_test(dt)
        self.assertEqual(timings.run_start_time, dt.timestamp())
        self.assertEqual(timings.current_test_start_time, dt.timestamp())

    def test_end_test_clears_current_test_time(self):
        timings = ResultTestTimings()
        dt = datetime(2023, 1, 1, 12, 0, 0)
        timings.start_test(dt)
        self.assertIsNotNone(timings.current_test_start_time)
        timings.end_test(dt)
        self.assertIsNone(timings.current_test_start_time)

    def test_end_suite_clears_time(self):
        timings = ResultTestTimings()
        dt = datetime(2023, 1, 1, 12, 0, 0)
        # Should not raise any errors, does essentially nothing
        timings.end_suite(dt)


class TestRebotTrace(unittest.TestCase):
    def setUp(self):
        self.args = RobotTraceArgs(verbosity="NORMAL", console_progress="NONE")
        self.trace = RebotTrace(self.args)
        self.trace.stats = MagicMock()
        self.trace.timings = MagicMock()
        self.trace.result_printer = MagicMock()

    def test_start_suite(self):
        self.trace.start_suite("Suite 1", {"starttime": datetime(2023, 1, 1)})
        self.trace.stats.start_suite.assert_called_once()
        self.trace.timings.start_suite.assert_called_once()
        self.trace.result_printer.start_suite.assert_called_once()

    def test_end_suite(self):
        self.trace.end_suite("Suite 1", {"endtime": datetime(2023, 1, 1)})
        self.trace.stats.end_suite.assert_called_once()
        self.trace.timings.end_suite.assert_called_once()
        self.trace.result_printer.end_suite.assert_called_once()

    def test_start_test(self):
        self.trace.start_test("Test 1", {"starttime": datetime(2023, 1, 1)})
        self.assertTrue(self.trace.in_test)
        self.trace.stats.start_test.assert_called_once()
        self.trace.timings.start_test.assert_called_once()
        self.trace.result_printer.start_test.assert_called_once()

    def test_end_test(self):
        self.trace.end_test("Test 1", {"endtime": datetime(2023, 1, 1)})
        self.assertFalse(self.trace.in_test)
        self.trace.stats.end_test.assert_called_once()
        self.trace.timings.end_test.assert_called_once()
        self.trace.result_printer.end_test.assert_called_once()

    def test_start_keyword(self):
        self.trace.start_keyword("Kw 1", {})
        self.trace.result_printer.start_keyword.assert_called_once()

    def test_end_keyword(self):
        self.trace.end_keyword("Kw 1", {})
        self.trace.result_printer.end_keyword.assert_called_once()

    def test_log_message_info(self):
        msg_attrs = {"level": "INFO", "message": "msg"}

        class MockMessage:
            level = "INFO"
            message = "msg"

        self.trace.log_message(MockMessage())
        self.trace.result_printer.log_message.assert_called_once_with(False, msg_attrs)
        self.trace.stats.log_error.assert_not_called()
        self.trace.stats.log_warning.assert_not_called()

    def test_log_message_warn(self):
        msg_attrs = {"level": "WARN", "message": "msg"}

        class MockMessage:
            level = "WARN"
            message = "msg"

        self.trace.log_message(MockMessage())
        self.trace.result_printer.log_message.assert_called_once_with(False, msg_attrs)
        self.trace.stats.log_warning.assert_called_once_with("msg")

    def test_log_message_error(self):
        msg_attrs = {"level": "ERROR", "message": "msg"}

        class MockMessage:
            level = "ERROR"
            message = "msg"

        self.trace.log_message(MockMessage())
        self.trace.result_printer.log_message.assert_called_once_with(False, msg_attrs)
        self.trace.stats.log_error.assert_called_once_with("msg")

    @patch("builtins.print")
    def test_end_result(self, mock_print):
        self.trace.stats.format_run_summary.return_value = "Run Summary"
        self.trace.stats.format_run_results.return_value = "Run Results"
        self.trace.timings.run_start_time = 123456789.0
        self.trace.timings.format_time.return_value = "10s"
        self.trace.end_result(10.0)

        mock_print.assert_any_call("RUN COMPLETE: Run Summary")
        mock_print.assert_any_call("\nRun Results")
        mock_print.assert_any_call("Total elapsed: 10s.")

    @patch("builtins.print")
    def test_end_result_quiet(self, mock_print):
        self.trace.args.verbosity = Verbosity.QUIET
        self.trace.stats.format_run_summary.return_value = "Run Summary"
        self.trace.stats.format_run_results.return_value = "Run Results"
        self.trace.timings.run_start_time = 123456789.0
        self.trace.timings.format_time.return_value = "10s"
        self.trace.end_result(10.0)

        mock_print.assert_called_once_with("RUN COMPLETE: Run Summary")


class TestResultVisitorListenerAdapter(unittest.TestCase):
    def setUp(self):
        self.listener = MagicMock()
        self.adapter = ResultVisitorListenerAdapter(self.listener)

    def test_start_suite(self):
        suite = MagicMock()
        suite.name = "Suite 1"
        suite.full_name = "Suite 1"
        suite.test_count = 0
        suite.start_time = "20230101 12:00:00.000"
        self.adapter.start_suite(suite)
        self.listener.start_suite.assert_called_once_with(
            "Suite 1",
            {
                "longname": "Suite 1",
                "totaltests": 0,
                "starttime": "20230101 12:00:00.000",
            },
        )

    def test_end_suite(self):
        suite = MagicMock()
        suite.name = "Suite 1"
        suite.full_name = "Suite 1"
        suite.test_count = 0
        suite.status = "PASS"
        suite.message = ""
        suite.elapsedtime = 1000
        suite.end_time = "20230101 12:00:01.000"
        self.adapter.end_suite(suite)
        self.listener.end_suite.assert_called_once_with(
            "Suite 1",
            {
                "longname": "Suite 1",
                "totaltests": 0,
                "status": "PASS",
                "message": "",
                "elapsedtime": 1000,
                "endtime": "20230101 12:00:01.000",
            },
        )

    def test_start_test(self):
        test = MagicMock()
        test.name = "Test 1"
        test.full_name = "Test 1"
        test.start_time = "20230101 12:00:00.000"
        self.adapter.start_test(test)
        self.listener.start_test.assert_called_once_with(
            "Test 1", {"longname": "Test 1", "starttime": "20230101 12:00:00.000"}
        )

    def test_end_test_pass(self):
        test = MagicMock()
        test.name = "Test 1"
        test.full_name = "Test 1"
        test.status = "PASS"
        test.message = ""
        test.elapsedtime = 1000
        test.end_time = "20230101 12:00:01.000"
        self.adapter.end_test(test)
        self.listener.end_test.assert_called_once_with(
            "Test 1",
            {
                "longname": "Test 1",
                "status": "PASS",
                "message": "",
                "elapsedtime": 1000,
                "endtime": "20230101 12:00:01.000",
            },
        )

    def test_end_test_fudged_pass(self):
        test = MagicMock()
        test.name = "Test 1"
        test.full_name = "Test 1"
        test.status = "FAIL"
        test.message = "Parent suite teardown failed: Error"
        test.elapsedtime = 1000
        test.end_time = "20230101 12:00:01.000"
        self.adapter.end_test(test)
        self.listener.end_test.assert_called_once_with(
            "Test 1",
            {
                "longname": "Test 1",
                "status": "PASS",
                "message": "Parent suite teardown failed: Error",
                "elapsedtime": 1000,
                "endtime": "20230101 12:00:01.000",
            },
        )

    def test_start_message(self):
        msg = MagicMock()
        msg.message = "Hello"
        msg.level = "INFO"
        self.adapter.start_message(msg)
        self.listener.log_message.assert_called_once_with(msg)

    def test_node_to_listener_keyword(self):
        kw = MagicMock(spec=Keyword)
        kw.full_name = "Kw 1"
        kw.name = "Kw 1"
        kw.status = "PASS"
        kw.elapsedtime = 1000
        kw.type = "KEYWORD"
        kw.kwname = "Kw 1"
        kw.owner = "Owner"
        kw.doc = "Doc"
        kw.args = ["a", "b"]
        kw.assign = []
        kw.tags = []
        name, attrs = self.adapter._node_to_listener_keyword(kw, is_end=False)
        self.assertEqual(name, "Kw 1")
        self.assertEqual(attrs["type"], "KEYWORD")
        self.assertEqual(attrs["status"], "NOT SET")
        self.assertEqual(attrs["elapsedtime"], 0)
        self.assertEqual(attrs["args"], ["a", "b"])

    def test_node_to_listener_keyword_for(self):
        node = MagicMock(spec=For)
        node.status = "PASS"
        node.elapsedtime = 1000
        node.assign = ["${x}"]
        node.flavor = "IN"
        node.values = ["1", "2"]
        node.start = ""
        node.mode = ""
        node.fill = ""
        name, attrs = self.adapter._node_to_listener_keyword(node)
        self.assertEqual(name, "${x}    IN    1    2")
        self.assertEqual(attrs["type"], "FOR")
        self.assertEqual(attrs["flavor"], "IN")

    def test_node_to_listener_keyword_if(self):
        node = MagicMock(spec=If)
        node.status = "PASS"
        node.elapsedtime = 1000
        name, attrs = self.adapter._node_to_listener_keyword(node)
        self.assertEqual(name, "")
        self.assertEqual(attrs["type"], "IF")

    def test_node_to_listener_keyword_if_branch(self):
        node = MagicMock(spec=IfBranch)
        node.status = "PASS"
        node.elapsedtime = 1000
        node.type = "ELSE IF"
        node.condition = "${x} > 1"
        name, attrs = self.adapter._node_to_listener_keyword(node)
        self.assertEqual(name, "${x} > 1")
        self.assertEqual(attrs["type"], "ELSE IF")

    def test_start_end_body_item(self):
        kw = MagicMock(spec=Keyword)
        kw.full_name = "Kw 1"
        kw.name = "Kw 1"
        kw.status = "PASS"
        kw.elapsedtime = 1000
        kw.type = "KEYWORD"
        kw.kwname = "Kw 1"
        kw.owner = "Owner"
        kw.doc = "Doc"
        kw.args = ["a", "b"]
        kw.assign = []
        kw.tags = []
        self.adapter._start_body_item(kw)
        self.listener.start_keyword.assert_called_once()
        self.adapter._end_body_item(kw)
        self.listener.end_keyword.assert_called_once()

    def test_visit_various_nodes(self):
        kw = MagicMock(spec=Keyword)
        kw.full_name = "Kw 1"
        kw.name = "Kw 1"
        kw.status = "PASS"
        kw.elapsedtime = 1000
        kw.type = "KEYWORD"
        kw.kwname = "Kw 1"
        kw.owner = "Owner"
        kw.doc = "Doc"
        kw.args = ["a", "b"]
        kw.assign = []
        kw.tags = []
        self.adapter.start_keyword(kw)
        self.adapter.end_keyword(kw)

        node_if = MagicMock(spec=If)
        self.adapter.start_if(node_if)  # Should pass

        br = MagicMock(spec=IfBranch)
        br.status = "PASS"
        br.elapsedtime = 1000
        br.type = "ELSE IF"
        br.condition = "${x} > 1"
        self.adapter.start_if_branch(br)
        self.adapter.end_if_branch(br)

        self.assertEqual(self.listener.start_keyword.call_count, 2)
        self.assertEqual(self.listener.end_keyword.call_count, 2)

    def test_visit_errors(self):
        self.adapter.visit_errors([])

    def test_end_result(self):
        result = MagicMock()
        result.suite.elapsed_time.total_seconds.return_value = 1.5
        self.adapter.end_result(result)
        self.listener.end_result.assert_called_once_with(1.5)

    def test_for_block(self):
        node = MagicMock(spec=For)
        node.status = "PASS"
        node.elapsedtime = 1000
        node.flavor = "IN"
        node.assign = ["${var}"]
        node.values = ["1", "2"]
        node.start = ""
        node.mode = ""
        node.fill = ""
        self.adapter.start_for(node)
        self.listener.start_keyword.assert_called_once()
        self.adapter.end_for(node)
        self.listener.end_keyword.assert_called_once()

    def test_for_iteration(self):
        node = MagicMock(spec=ForIteration)
        node.status = "PASS"
        node.elapsedtime = 1000
        node.assign = {"${var}": "1"}
        self.adapter.start_for_iteration(node)
        self.listener.start_keyword.assert_called_once()
        self.adapter.end_for_iteration(node)
        self.listener.end_keyword.assert_called_once()

    def test_if_structure(self):
        node = MagicMock(spec=If)
        node.status = "PASS"
        node.elapsedtime = 1000
        self.adapter.start_if(node)
        # start_if should NOT call start_keyword
        self.listener.start_keyword.assert_not_called()
        self.adapter.end_if(node)
        self.listener.end_keyword.assert_not_called()

    def test_try_structure(self):
        node = MagicMock(spec=Try)
        node.status = "PASS"
        node.elapsedtime = 1000
        self.adapter.start_try(node)
        # start_try should NOT call start_keyword
        self.listener.start_keyword.assert_not_called()
        self.adapter.end_try(node)
        self.listener.end_keyword.assert_not_called()

    def test_try_branch(self):
        node = MagicMock(spec=TryBranch)
        node.status = "PASS"
        node.elapsedtime = 1000
        node.type = "EXCEPT"
        node.patterns = []
        node.pattern_type = ""
        node.assign = ""
        self.adapter.start_try_branch(node)
        self.listener.start_keyword.assert_called_once()
        self.adapter.end_try_branch(node)
        self.listener.end_keyword.assert_called_once()

    def test_while(self):
        node = MagicMock(spec=While)
        node.status = "PASS"
        node.elapsedtime = 1000
        node.condition = "${True}"
        node.limit = ""
        node.on_limit = ""
        node.on_limit_message = ""
        self.adapter.start_while(node)
        self.listener.start_keyword.assert_called_once()
        self.adapter.end_while(node)
        self.listener.end_keyword.assert_called_once()

    def test_while_iteration(self):
        node = MagicMock(spec=WhileIteration)
        node.status = "PASS"
        node.elapsedtime = 1000
        self.adapter.start_while_iteration(node)
        self.listener.start_keyword.assert_called_once()
        self.adapter.end_while_iteration(node)
        self.listener.end_keyword.assert_called_once()

    def test_group(self):
        node = MagicMock(spec=Group)
        node.status = "PASS"
        node.elapsedtime = 1000
        node.name = "My Group"
        self.adapter.start_group(node)
        self.listener.start_keyword.assert_called_once()
        self.adapter.end_group(node)
        self.listener.end_keyword.assert_called_once()

    def test_var(self):
        node = MagicMock(spec=Var)
        node.status = "PASS"
        node.elapsedtime = 1000
        node.name = "${x}"
        node.value = ["1"]
        node.scope = ""
        self.adapter.start_var(node)
        self.listener.start_keyword.assert_called_once()
        self.adapter.end_var(node)
        self.listener.end_keyword.assert_called_once()

    def test_return(self):
        node = MagicMock(spec=Return)
        node.status = "PASS"
        node.elapsedtime = 1000
        node.values = []
        self.adapter.start_return(node)
        self.listener.start_keyword.assert_called_once()
        self.adapter.end_return(node)
        self.listener.end_keyword.assert_called_once()

    def test_continue(self):
        node = MagicMock(spec=Continue)
        node.status = "PASS"
        node.elapsedtime = 1000
        self.adapter.start_continue(node)
        self.listener.start_keyword.assert_called_once()
        self.adapter.end_continue(node)
        self.listener.end_keyword.assert_called_once()

    def test_break(self):
        node = MagicMock(spec=Break)
        node.status = "PASS"
        node.elapsedtime = 1000
        self.adapter.start_break(node)
        self.listener.start_keyword.assert_called_once()
        self.adapter.end_break(node)
        self.listener.end_keyword.assert_called_once()

    def test_error(self):
        node = MagicMock(spec=Error)
        node.status = "PASS"
        node.elapsedtime = 1000
        node.values = []
        self.adapter.start_error(node)
        self.listener.start_keyword.assert_called_once()
        self.adapter.end_error(node)
        self.listener.end_keyword.assert_called_once()

    def test_node_to_listener_keyword_for_iteration(self):
        node = MagicMock(spec=ForIteration)
        node.status = "PASS"
        node.elapsedtime = 1000
        node.assign = {"${x}": "1"}
        name, attrs = self.adapter._node_to_listener_keyword(node)
        self.assertEqual(name, "${x} = 1")
        self.assertEqual(attrs["type"], "ITERATION")

    def test_node_to_listener_keyword_while(self):
        node = MagicMock(spec=While)
        node.status = "PASS"
        node.elapsedtime = 1000
        node.condition = "${x} < 10"
        node.limit = "100"
        node.on_limit = "pass"
        node.on_limit_message = "Limit hit"
        name, attrs = self.adapter._node_to_listener_keyword(node)
        self.assertEqual(name, "${x} < 10")
        self.assertEqual(attrs["type"], "WHILE")

    def test_node_to_listener_keyword_while_iteration(self):
        node = MagicMock(spec=WhileIteration)
        node.status = "PASS"
        node.elapsedtime = 1000
        name, attrs = self.adapter._node_to_listener_keyword(node)
        self.assertEqual(name, "")
        self.assertEqual(attrs["type"], "ITERATION")

    def test_node_to_listener_keyword_group(self):
        node = MagicMock(spec=Group)
        node.status = "PASS"
        node.elapsedtime = 1000
        node.name = "Group Name"
        name, attrs = self.adapter._node_to_listener_keyword(node)
        self.assertEqual(name, "Group Name")
        self.assertEqual(attrs["type"], "GROUP")

    def test_node_to_listener_keyword_try(self):
        node = MagicMock(spec=Try)
        node.status = "PASS"
        node.elapsedtime = 1000
        name, attrs = self.adapter._node_to_listener_keyword(node)
        self.assertEqual(name, "")
        self.assertEqual(attrs["type"], "TRY")

    def test_node_to_listener_keyword_try_branch(self):
        node = MagicMock(spec=TryBranch)
        node.status = "PASS"
        node.elapsedtime = 1000
        node.type = "EXCEPT"
        node.patterns = ["ValueError"]
        node.pattern_type = "glob"
        node.assign = "${err}"
        name, attrs = self.adapter._node_to_listener_keyword(node)
        self.assertEqual(name, "")
        self.assertEqual(attrs["type"], "EXCEPT")
        self.assertEqual(attrs["patterns"], ["ValueError"])

    def test_node_to_listener_keyword_var(self):
        node = MagicMock(spec=Var)
        node.status = "PASS"
        node.elapsedtime = 1000
        node.name = "${x}"
        node.value = ["1", "2"]
        node.scope = "SUITE"
        name, attrs = self.adapter._node_to_listener_keyword(node)
        self.assertEqual(name, "${x}    1    2")
        self.assertEqual(attrs["type"], "VAR")
        self.assertEqual(attrs["value"], ["1", "2"])

    def test_node_to_listener_keyword_return(self):
        node = MagicMock(spec=Return)
        node.status = "PASS"
        node.elapsedtime = 1000
        node.values = ["${x}"]
        name, attrs = self.adapter._node_to_listener_keyword(node)
        self.assertEqual(name, "")
        self.assertEqual(attrs["type"], "RETURN")

    def test_node_to_listener_keyword_continue(self):
        node = MagicMock(spec=Continue)
        node.status = "PASS"
        node.elapsedtime = 1000
        name, attrs = self.adapter._node_to_listener_keyword(node)
        self.assertEqual(name, "")
        self.assertEqual(attrs["type"], "CONTINUE")

    def test_node_to_listener_keyword_break(self):
        node = MagicMock(spec=Break)
        node.status = "PASS"
        node.elapsedtime = 1000
        name, attrs = self.adapter._node_to_listener_keyword(node)
        self.assertEqual(name, "")
        self.assertEqual(attrs["type"], "BREAK")

    def test_node_to_listener_keyword_error(self):
        node = MagicMock(spec=Error)
        node.status = "PASS"
        node.elapsedtime = 1000
        node.values = ["msg"]
        name, attrs = self.adapter._node_to_listener_keyword(node)
        self.assertEqual(name, "")
        self.assertEqual(attrs["type"], "ERROR")

    def test_node_to_listener_keyword_fallback(self):
        class UnknownNode:
            def __init__(self):
                self.full_name = "Unknown"
                self.type = "UNKNOWN_TYPE"
                self.status = "PASS"
                self.elapsedtime = 1000

        node = UnknownNode()
        name, attrs = self.adapter._node_to_listener_keyword(node)
        self.assertEqual(name, "Unknown")
        self.assertEqual(attrs["type"], "UNKNOWN_TYPE")


if __name__ == "__main__":
    unittest.main()
