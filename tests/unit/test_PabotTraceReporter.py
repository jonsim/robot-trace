# Unit tests for PabotTraceReporter.py.
#
# Copyright (c) 2026 Jonathan Simmonds
import sys
import unittest
from io import StringIO
from unittest.mock import MagicMock, patch

from pabot_trace.PabotTraceReporter import PabotTraceReporter


class PabotTraceReporterTestBase(unittest.TestCase):
    """Suppress unexpected stdout/stderr output during tests."""

    def setUp(self):
        super().setUp()
        self.orig_stdout = sys.__stdout__
        self.orig_stderr = sys.__stderr__
        sys.__stdout__ = StringIO()
        sys.__stderr__ = StringIO()
        self.env_patcher = patch.dict(
            "os.environ", {"_PABOT_TRACE_COLLECTOR_PORT": "5292"}
        )
        self.env_patcher.start()

    def tearDown(self):
        self.env_patcher.stop()
        super().tearDown()
        sys.__stdout__ = self.orig_stdout
        sys.__stderr__ = self.orig_stderr


class TestPabotTraceReporterInit(PabotTraceReporterTestBase):
    def setUp(self):
        super().setUp()
        with patch(
            "pabot_trace.PabotTraceReporter.ServerProxy", return_value=MagicMock()
        ):
            self.reporter = PabotTraceReporter()

    def test_uid_initially_none(self):
        self.assertIsNone(self.reporter._uid)

    def test_queue_index_initially_none(self):
        self.assertIsNone(self.reporter._queue_index)

    def test_pool_id_initially_none(self):
        self.assertIsNone(self.reporter._pool_id)

    def test_process_count_initially_none(self):
        self.assertIsNone(self.reporter._process_count)

    def test_proxy_created(self):
        self.assertIsNotNone(self.reporter.proxy)


class TestPabotTraceReporterPrintTrace(PabotTraceReporterTestBase):
    def setUp(self):
        super().setUp()
        self.mock_proxy = MagicMock()
        with patch(
            "pabot_trace.PabotTraceReporter.ServerProxy",
            return_value=self.mock_proxy,
        ):
            self.reporter = PabotTraceReporter()
        self.reporter._uid = "test-uid"
        self.reporter._pool_id = 1
        self.reporter._queue_index = 2

    def test_print_trace_encodes_text_as_binary(self):
        from xmlrpc.client import Binary

        self.reporter._print_trace("hello trace")
        args = self.mock_proxy.print_trace.call_args[0]
        # 4th arg should be a Binary wrapping the UTF-8 encoded text
        self.assertIsInstance(args[3], Binary)
        self.assertEqual(args[3].data, b"hello trace")

    def test_print_trace_passes_uid(self):
        self.reporter._print_trace("text")
        args = self.mock_proxy.print_trace.call_args[0]
        self.assertEqual(args[0], "test-uid")

    def test_print_trace_passes_pool_id(self):
        self.reporter._print_trace("text")
        args = self.mock_proxy.print_trace.call_args[0]
        self.assertEqual(args[1], 1)

    def test_print_trace_passes_queue_index(self):
        self.reporter._print_trace("text")
        args = self.mock_proxy.print_trace.call_args[0]
        self.assertEqual(args[2], 2)

    def test_print_trace_handles_unicode(self):
        self.reporter._print_trace("héllo wörld")
        args = self.mock_proxy.print_trace.call_args[0]
        self.assertEqual(args[3].data, "héllo wörld".encode())


class TestPabotTraceReporterRecordId(PabotTraceReporterTestBase):
    def setUp(self):
        super().setUp()
        self.mock_proxy = MagicMock()
        with patch(
            "pabot_trace.PabotTraceReporter.ServerProxy",
            return_value=self.mock_proxy,
        ):
            self.reporter = PabotTraceReporter()

        self.mock_builtin = MagicMock()
        self.mock_builtin.get_variable_value.side_effect = lambda var: {
            r"${CALLER_ID}": "uid-42",
            r"${PABOTQUEUEINDEX}": "3",
            r"${PABOTEXECUTIONPOOLID}": "7",
            r"${PABOTNUMBEROFPROCESSES}": "8",
        }[var]

        self.builtin_patcher = patch(
            "robot.libraries.BuiltIn.BuiltIn",
            return_value=self.mock_builtin,
        )
        self.builtin_patcher.start()

    def tearDown(self):
        self.builtin_patcher.stop()
        super().tearDown()

    def test_record_id_sets_uid(self):
        self.reporter._record_id()
        self.assertEqual(self.reporter._uid, "uid-42")

    def test_record_id_sets_queue_index(self):
        self.reporter._record_id()
        self.assertEqual(self.reporter._queue_index, 3)

    def test_record_id_sets_pool_id(self):
        self.reporter._record_id()
        self.assertEqual(self.reporter._pool_id, 7)

    def test_record_id_sets_process_count(self):
        self.reporter._record_id()
        self.assertEqual(self.reporter._process_count, 8)

    def test_record_id_calls_report_context(self):
        self.reporter._record_id()
        self.mock_proxy.report_context.assert_called_once()

    def test_record_id_report_context_includes_uid(self):
        self.reporter._record_id()
        context = self.mock_proxy.report_context.call_args[0][0]
        self.assertEqual(context["uid"], "uid-42")

    def test_record_id_report_context_includes_pool_id(self):
        self.reporter._record_id()
        context = self.mock_proxy.report_context.call_args[0][0]
        self.assertEqual(context["pool_id"], 7)

    def test_record_id_report_context_includes_queue_index(self):
        self.reporter._record_id()
        context = self.mock_proxy.report_context.call_args[0][0]
        self.assertEqual(context["queue_index"], 3)

    def test_record_id_report_context_includes_process_count(self):
        self.reporter._record_id()
        context = self.mock_proxy.report_context.call_args[0][0]
        self.assertEqual(context["process_count"], 8)


class TestPabotTraceReporterStartSuite(PabotTraceReporterTestBase):
    def setUp(self):
        super().setUp()
        self.mock_proxy = MagicMock()
        with patch(
            "pabot_trace.PabotTraceReporter.ServerProxy",
            return_value=self.mock_proxy,
        ):
            self.reporter = PabotTraceReporter()

        self.mock_builtin = MagicMock()
        self.mock_builtin.get_variable_value.side_effect = lambda var: {
            r"${CALLER_ID}": "uid-1",
            r"${PABOTQUEUEINDEX}": "0",
            r"${PABOTEXECUTIONPOOLID}": "0",
            r"${PABOTNUMBEROFPROCESSES}": "2",
        }[var]

        self.builtin_patcher = patch(
            "robot.libraries.BuiltIn.BuiltIn",
            return_value=self.mock_builtin,
        )
        self.builtin_patcher.start()

    def tearDown(self):
        self.builtin_patcher.stop()
        super().tearDown()

    def _suite_attrs(self):
        return {"suites": [], "totaltests": 1, "longname": "My Suite"}

    def test_start_suite_records_id_when_uid_unset(self):
        self.reporter.start_suite("My Suite", self._suite_attrs())
        self.assertEqual(self.reporter._uid, "uid-1")

    def test_start_suite_does_not_re_record_id_when_uid_already_set(self):
        self.reporter._uid = "existing-uid"
        self.reporter._pool_id = 0
        self.reporter._queue_index = 0
        self.reporter.start_suite("My Suite", self._suite_attrs())
        self.mock_proxy.report_context.assert_not_called()

    def test_start_suite_calls_proxy_start_suite(self):
        attrs = self._suite_attrs()
        self.reporter.start_suite("My Suite", attrs)
        self.mock_proxy.start_suite.assert_called_once_with(
            "uid-1", 0, 0, "My Suite", attrs
        )

    def test_start_suite_calls_super(self):
        attrs = self._suite_attrs()
        self.reporter.start_suite("My Suite", attrs)
        # super().start_suite populates started_suites
        self.assertIn("My Suite", self.reporter.stats.started_suites)


class TestPabotTraceReporterEndSuite(PabotTraceReporterTestBase):
    def setUp(self):
        super().setUp()
        self.mock_proxy = MagicMock()
        with patch(
            "pabot_trace.PabotTraceReporter.ServerProxy",
            return_value=self.mock_proxy,
        ):
            self.reporter = PabotTraceReporter()
        self.reporter._uid = "uid-1"
        self.reporter._pool_id = 0
        self.reporter._queue_index = 0

    def test_end_suite_calls_proxy_end_suite(self):
        attrs = {"status": "PASS", "longname": "My Suite"}
        self.reporter.end_suite("My Suite", attrs)
        self.mock_proxy.end_suite.assert_called_once_with(
            "uid-1", 0, 0, "My Suite", attrs
        )

    def test_end_suite_calls_super(self):
        attrs = {"suites": [], "totaltests": 1, "longname": "My Suite"}
        self.reporter.start_suite("My Suite", attrs)
        end_attrs = {"status": "PASS", "longname": "My Suite", "message": ""}
        self.reporter.end_suite("My Suite", end_attrs)
        # If super ran, result_printer's suite_trace_stack depth should be 0
        self.assertEqual(self.reporter.result_printer.suite_trace_stack._depth, 0)


class TestPabotTraceReporterStartTest(PabotTraceReporterTestBase):
    def setUp(self):
        super().setUp()
        self.mock_proxy = MagicMock()
        with patch(
            "pabot_trace.PabotTraceReporter.ServerProxy",
            return_value=self.mock_proxy,
        ):
            self.reporter = PabotTraceReporter()
        self.reporter._uid = "uid-1"
        self.reporter._pool_id = 0
        self.reporter._queue_index = 0

        suite_attrs = {"suites": [], "totaltests": 1, "longname": "My Suite"}
        self.reporter.start_suite("My Suite", suite_attrs)

    def test_start_test_calls_proxy_start_test(self):
        attrs = {"longname": "My Suite.My Test"}
        self.reporter.start_test("My Test", attrs)
        self.mock_proxy.start_test.assert_called_once_with(
            "uid-1", 0, 0, "My Test", attrs
        )

    def test_start_test_calls_super(self):
        attrs = {"longname": "My Suite.My Test"}
        self.reporter.start_test("My Test", attrs)
        self.assertTrue(self.reporter.in_test)


class TestPabotTraceReporterEndTest(PabotTraceReporterTestBase):
    def setUp(self):
        super().setUp()
        self.mock_proxy = MagicMock()
        with patch(
            "pabot_trace.PabotTraceReporter.ServerProxy",
            return_value=self.mock_proxy,
        ):
            self.reporter = PabotTraceReporter()
        self.reporter._uid = "uid-1"
        self.reporter._pool_id = 0
        self.reporter._queue_index = 0

        suite_attrs = {"suites": [], "totaltests": 1, "longname": "My Suite"}
        self.reporter.start_suite("My Suite", suite_attrs)
        self.reporter.start_test("My Test", {"longname": "My Suite.My Test"})

    def test_end_test_calls_proxy_end_test(self):
        attrs = {"status": "PASS", "longname": "My Suite.My Test", "message": ""}
        self.reporter.end_test("My Test", attrs)
        self.mock_proxy.end_test.assert_called_once_with(
            "uid-1", 0, 0, "My Test", attrs
        )

    def test_end_test_calls_super_clears_in_test(self):
        attrs = {"status": "PASS", "longname": "My Suite.My Test", "message": ""}
        self.reporter.end_test("My Test", attrs)
        self.assertFalse(self.reporter.in_test)

    def test_end_test_pass_updates_stats(self):
        attrs = {"status": "PASS", "longname": "My Suite.My Test", "message": ""}
        self.reporter.end_test("My Test", attrs)
        self.assertEqual(len(self.reporter.stats.passed_tests), 1)

    def test_end_test_fail_updates_stats(self):
        attrs = {"status": "FAIL", "longname": "My Suite.My Test", "message": "fail"}
        self.reporter.end_test("My Test", attrs)
        self.assertEqual(len(self.reporter.stats.failed_tests), 1)


class TestPabotTraceReporterLogMessage(PabotTraceReporterTestBase):
    def setUp(self):
        super().setUp()
        self.mock_proxy = MagicMock()
        with patch(
            "pabot_trace.PabotTraceReporter.ServerProxy",
            return_value=self.mock_proxy,
        ):
            self.reporter = PabotTraceReporter()
        self.reporter._uid = "uid-1"
        self.reporter._pool_id = 0
        self.reporter._queue_index = 0

        suite_attrs = {"suites": [], "totaltests": 1, "longname": "My Suite"}
        self.reporter.start_suite("My Suite", suite_attrs)
        self.reporter.start_test("My Test", {"longname": "My Suite.My Test"})

    def test_log_message_error_calls_proxy_log_error(self):
        self.reporter.log_message({"level": "ERROR", "message": "Something broke"})
        self.mock_proxy.log_error.assert_called_once_with(
            "uid-1", 0, 0, "Something broke"
        )

    def test_log_message_warn_calls_proxy_log_warning(self):
        self.reporter.log_message({"level": "WARN", "message": "Something shaky"})
        self.mock_proxy.log_warning.assert_called_once_with(
            "uid-1", 0, 0, "Something shaky"
        )

    def test_log_message_info_does_not_call_proxy(self):
        self.reporter.log_message({"level": "INFO", "message": "Just info"})
        self.mock_proxy.log_error.assert_not_called()
        self.mock_proxy.log_warning.assert_not_called()

    def test_log_message_debug_does_not_call_proxy(self):
        self.reporter.log_message({"level": "DEBUG", "message": "Debugging"})
        self.mock_proxy.log_error.assert_not_called()
        self.mock_proxy.log_warning.assert_not_called()

    def test_log_message_error_also_calls_super(self):
        self.reporter.log_message({"level": "ERROR", "message": "Something broke"})
        # super().log_message updates stats.errors
        self.assertEqual(len(self.reporter.stats.errors), 1)

    def test_log_message_warn_also_calls_super(self):
        self.reporter.log_message({"level": "WARN", "message": "Something shaky"})
        # super().log_message updates stats.warnings
        self.assertEqual(len(self.reporter.stats.warnings), 1)
