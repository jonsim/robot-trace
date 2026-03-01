import unittest
from io import StringIO
from unittest.mock import MagicMock, patch

from pabot_trace.PabotTraceCollector import (
    ExecutorProgressBox,
    PabotTraceCollector,
    StreamedTracePrinter,
    ThreadedTestStatistics,
)
from robot_trace.RobotTrace import ProgressBox

# ---------------------------------------------------------------------------
# ThreadedTestStatistics
# ---------------------------------------------------------------------------


class TestThreadedTestStatisticsEmpty(unittest.TestCase):
    def setUp(self):
        self.stats = ThreadedTestStatistics()

    def test_initial_test_count_is_none(self):
        self.assertIsNone(self.stats.top_level_test_count)

    def test_initial_started_tests_empty(self):
        self.assertEqual(self.stats.started_tests, [])

    def test_initial_passed_tests_empty(self):
        self.assertEqual(self.stats.passed_tests, [])

    def test_initial_skipped_tests_empty(self):
        self.assertEqual(self.stats.skipped_tests, [])

    def test_initial_failed_tests_empty(self):
        self.assertEqual(self.stats.failed_tests, [])

    def test_initial_completed_tests_empty(self):
        self.assertEqual(self.stats.completed_tests, [])

    def test_initial_started_suites_empty(self):
        self.assertEqual(self.stats.started_suites, [])

    def test_initial_completed_suites_empty(self):
        self.assertEqual(self.stats.completed_suites, [])

    def test_initial_warnings_empty(self):
        self.assertEqual(self.stats.warnings, {})

    def test_initial_errors_empty(self):
        self.assertEqual(self.stats.errors, {})


class TestThreadedTestStatisticsGetSuite(unittest.TestCase):
    def setUp(self):
        self.stats = ThreadedTestStatistics()

    def test_get_suite_statistics_creates_on_first_access(self):
        self.stats._get_suite_statistics("uid-1")
        self.assertIn("uid-1", self.stats._stats)

    def test_get_suite_statistics_returns_same_object(self):
        suite1 = self.stats._get_suite_statistics("uid-1")
        suite2 = self.stats._get_suite_statistics("uid-1")
        self.assertIs(suite1, suite2)

    def test_get_suite_statistics_separate_uids_are_independent(self):
        suite1 = self.stats._get_suite_statistics("uid-1")
        suite2 = self.stats._get_suite_statistics("uid-2")
        self.assertIsNot(suite1, suite2)


class TestThreadedTestStatisticsStartSuite(unittest.TestCase):
    def setUp(self):
        self.stats = ThreadedTestStatistics()

    def test_start_suite_records_in_correct_uid_bucket(self):
        self.stats.start_suite(
            "uid-1", "Suite A", {"suites": [], "totaltests": 3, "longname": "Suite A"}
        )
        self.assertIn("Suite A", self.stats.started_suites)

    def test_start_suite_different_uids_aggregate(self):
        self.stats.start_suite(
            "uid-1", "Suite A", {"suites": [], "totaltests": 1, "longname": "Suite A"}
        )
        self.stats.start_suite(
            "uid-2", "Suite B", {"suites": [], "totaltests": 1, "longname": "Suite B"}
        )
        self.assertIn("Suite A", self.stats.started_suites)
        self.assertIn("Suite B", self.stats.started_suites)


class TestThreadedTestStatisticsStartEndTest(unittest.TestCase):
    def setUp(self):
        self.stats = ThreadedTestStatistics()

    def test_start_test_adds_to_started_tests(self):
        self.stats.start_test("uid-1", "Test 1", {"longname": "Suite.Test 1"})
        self.assertEqual(len(self.stats.started_tests), 1)

    def test_end_test_pass_adds_to_passed_and_completed(self):
        self.stats.end_test(
            "uid-1", "Test 1", {"status": "PASS", "longname": "Suite.Test 1"}
        )
        self.assertEqual(len(self.stats.passed_tests), 1)
        self.assertEqual(len(self.stats.completed_tests), 1)

    def test_end_test_fail_adds_to_failed_and_completed(self):
        self.stats.end_test(
            "uid-1", "Test 1", {"status": "FAIL", "longname": "Suite.Test 1"}
        )
        self.assertEqual(len(self.stats.failed_tests), 1)
        self.assertEqual(len(self.stats.completed_tests), 1)

    def test_end_test_skip_adds_to_skipped_and_completed(self):
        self.stats.end_test(
            "uid-1", "Test 1", {"status": "SKIP", "longname": "Suite.Test 1"}
        )
        self.assertEqual(len(self.stats.skipped_tests), 1)
        self.assertEqual(len(self.stats.completed_tests), 1)

    def test_end_tests_from_multiple_uids_aggregate(self):
        self.stats.end_test(
            "uid-1", "Test 1", {"status": "PASS", "longname": "Suite.Test 1"}
        )
        self.stats.end_test(
            "uid-2", "Test 2", {"status": "FAIL", "longname": "Suite.Test 2"}
        )
        self.assertEqual(len(self.stats.passed_tests), 1)
        self.assertEqual(len(self.stats.failed_tests), 1)
        self.assertEqual(len(self.stats.completed_tests), 2)


class TestThreadedTestStatisticsWarningsErrors(unittest.TestCase):
    def setUp(self):
        self.stats = ThreadedTestStatistics()

    def test_log_warning_creates_entry(self):
        self.stats.start_test("uid-1", "Test 1", {"longname": "Suite.Test 1"})
        self.stats.log_warning("uid-1", "Something went wrong")
        self.assertEqual(len(self.stats.warnings), 1)

    def test_log_error_creates_entry(self):
        self.stats.start_test("uid-1", "Test 1", {"longname": "Suite.Test 1"})
        self.stats.log_error("uid-1", "Fatal error")
        self.assertEqual(len(self.stats.errors), 1)

    def test_warnings_from_multiple_uids_aggregate(self):
        self.stats.start_test("uid-1", "Test 1", {"longname": "Suite.Test 1"})
        self.stats.start_test("uid-2", "Test 2", {"longname": "Suite.Test 2"})
        self.stats.log_warning("uid-1", "Warn 1")
        self.stats.log_warning("uid-2", "Warn 2")
        self.assertEqual(len(self.stats.warnings), 2)

    def test_errors_from_multiple_uids_aggregate(self):
        self.stats.start_test("uid-1", "Test 1", {"longname": "Suite.Test 1"})
        self.stats.start_test("uid-2", "Test 2", {"longname": "Suite.Test 2"})
        self.stats.log_error("uid-1", "Error 1")
        self.stats.log_error("uid-2", "Error 2")
        self.assertEqual(len(self.stats.errors), 2)


# ---------------------------------------------------------------------------
# ExecutorProgressBox
# ---------------------------------------------------------------------------


class TestExecutorProgressBoxInit(unittest.TestCase):
    def setUp(self):
        self.stream = StringIO()

    def test_two_executors_creates_one_status_line(self):
        box = ExecutorProgressBox(self.stream, executors=2, colors=False, width=80)
        self.assertEqual(len(box._lines), 1)

    def test_three_executors_creates_two_status_lines(self):
        box = ExecutorProgressBox(self.stream, executors=3, colors=False, width=80)
        self.assertEqual(len(box._lines), 2)

    def test_four_executors_creates_two_status_lines(self):
        box = ExecutorProgressBox(self.stream, executors=4, colors=False, width=80)
        self.assertEqual(len(box._lines), 2)

    def test_top_border_contains_middle_divider(self):
        box = ExecutorProgressBox(self.stream, executors=2, colors=False, width=80)
        self.assertIn("┬", box._top_border)

    def test_bottom_border_contains_middle_divider(self):
        box = ExecutorProgressBox(self.stream, executors=2, colors=False, width=80)
        self.assertIn("┴", box._bottom_border)

    def test_executor_statuses_initialized_empty(self):
        box = ExecutorProgressBox(self.stream, executors=4, colors=False, width=80)
        self.assertEqual(box._executor_statuses, ["", "", "", ""])


class TestExecutorProgressBoxWriteStatus(unittest.TestCase):
    def setUp(self):
        self.stream = StringIO()
        self.box = ExecutorProgressBox(self.stream, executors=4, colors=False, width=80)

    def test_write_status_updates_internal_state(self):
        self.box.write_executor_status(0, "running")
        self.assertEqual(self.box._executor_statuses[0], "running")

    def test_write_status_second_executor_updates_state(self):
        self.box.write_executor_status(1, "waiting")
        self.assertEqual(self.box._executor_statuses[1], "waiting")

    def test_write_status_writes_to_stream(self):
        # Clear stream after init
        self.stream.truncate(0)
        self.stream.seek(0)
        self.box.write_executor_status(0, "running test")
        output = self.stream.getvalue()
        self.assertIn("running test", output)

    def test_write_status_out_of_range_raises(self):
        with self.assertRaises(AssertionError):
            self.box.write_executor_status(4, "x")

    def test_write_status_none_stream_does_not_raise(self):
        box = ExecutorProgressBox(None, executors=2, colors=False, width=80)
        box.write_executor_status(0, "status")  # should not raise

    def test_write_right_executor_formatted_on_same_line_as_left(self):
        self.stream.truncate(0)
        self.stream.seek(0)
        self.box.write_executor_status(0, "LEFT")
        self.stream.truncate(0)
        self.stream.seek(0)
        self.box.write_executor_status(1, "RIGHT")
        output = self.stream.getvalue()
        # Both left and right with '│' separating them should appear
        self.assertIn("│", output)

    def test_odd_executor_shows_empty_right_side_for_last_solo(self):
        box = ExecutorProgressBox(self.stream, executors=3, colors=False, width=80)
        self.stream.truncate(0)
        self.stream.seek(0)
        box.write_executor_status(2, "SOLO")
        output = self.stream.getvalue()
        self.assertIn("SOLO", output)


class TestExecutorProgressBoxFormatId(unittest.TestCase):
    def setUp(self):
        self.stream = StringIO()

    def test_format_id_less_than_10_short(self):
        box = ExecutorProgressBox(self.stream, executors=4, colors=False, width=80)
        # Access via StreamedTracePrinter since format_executor_id lives there
        printer = StreamedTracePrinter(box, ThreadedTestStatistics(), lambda x: None)
        result = printer._format_executor_id(1, 2)
        self.assertEqual(result, "[1][ 2]")

    def test_format_id_10_to_99_medium(self):
        box = ExecutorProgressBox(self.stream, executors=50, colors=False, width=80)
        printer = StreamedTracePrinter(box, ThreadedTestStatistics(), lambda x: None)
        result = printer._format_executor_id(10, 5)
        self.assertEqual(result, "[10][ 5]")

    def test_format_id_100_plus_long(self):
        box = ExecutorProgressBox(self.stream, executors=150, colors=False, width=160)
        printer = StreamedTracePrinter(box, ThreadedTestStatistics(), lambda x: None)
        result = printer._format_executor_id(100, 5)
        self.assertEqual(result, "[100][  5]")


# ---------------------------------------------------------------------------
# StreamedTracePrinter
# ---------------------------------------------------------------------------


class TestStreamedTracePrinterBase(unittest.TestCase):
    def setUp(self):
        self.stream = StringIO()
        self.progress_box = ExecutorProgressBox(
            self.stream, executors=2, colors=False, width=80
        )
        self.stats = ThreadedTestStatistics()
        self.printed = []
        self.printer = StreamedTracePrinter(
            self.progress_box, self.stats, self.printed.append
        )

    def _suite_attrs(self, name):
        return {"suites": [], "totaltests": 1, "longname": name}

    def _test_attrs(self, longname):
        return {"longname": longname}

    def _end_test_attrs(self, status, longname):
        return {"status": status, "longname": longname}


class TestStreamedTracePrinterReportTestCount(TestStreamedTracePrinterBase):
    def test_sets_top_level_test_count(self):
        self.printer.report_test_count(42)
        self.assertEqual(self.stats.top_level_test_count, 42)

    def test_sets_progress_box_total_tasks(self):
        self.printer.report_test_count(10)
        self.assertEqual(self.progress_box.total_tasks, 10)


class TestStreamedTracePrinterReportContext(TestStreamedTracePrinterBase):
    def test_report_context_does_not_raise(self):
        self.printer.report_context({"uid": "abc", "pool_id": 0})


class TestStreamedTracePrinterStartSuite(TestStreamedTracePrinterBase):
    def test_start_suite_updates_stats(self):
        self.printer.start_suite("uid-1", 0, 0, "MySuite", self._suite_attrs("MySuite"))
        self.assertIn("MySuite", self.stats.started_suites)

    def test_start_suite_writes_executor_status(self):
        self.stream.truncate(0)
        self.stream.seek(0)
        self.printer.start_suite("uid-1", 0, 0, "MySuite", self._suite_attrs("MySuite"))
        output = self.stream.getvalue()
        self.assertIn("[SUITE]", output)
        self.assertIn("MySuite", output)


class TestStreamedTracePrinterEndSuite(TestStreamedTracePrinterBase):
    def test_end_suite_updates_stats(self):
        self.printer.start_suite("uid-1", 0, 0, "MySuite", self._suite_attrs("MySuite"))
        self.printer.end_suite(
            "uid-1", 0, 0, "MySuite", {"status": "PASS", "longname": "MySuite"}
        )
        self.assertIn("MySuite", self.stats.completed_suites)

    def test_end_suite_clears_executor_status(self):
        self.printer.start_suite("uid-1", 0, 0, "MySuite", self._suite_attrs("MySuite"))
        self.stream.truncate(0)
        self.stream.seek(0)
        self.printer.end_suite(
            "uid-1", 0, 0, "MySuite", {"status": "PASS", "longname": "MySuite"}
        )
        self.assertEqual(self.progress_box._executor_statuses[0], "[0][ 0]")


class TestStreamedTracePrinterStartTest(TestStreamedTracePrinterBase):
    def test_start_test_updates_stats(self):
        self.printer.start_test(
            "uid-1", 0, 0, "Test 1", self._test_attrs("Suite.Test 1")
        )
        self.assertEqual(len(self.stats.started_tests), 1)

    def test_start_test_writes_executor_status(self):
        self.stream.truncate(0)
        self.stream.seek(0)
        self.printer.start_test(
            "uid-1", 0, 0, "Test 1", self._test_attrs("Suite.Test 1")
        )
        output = self.stream.getvalue()
        self.assertIn("[TEST]", output)
        self.assertIn("Test 1", output)


class TestStreamedTracePrinterEndTest(TestStreamedTracePrinterBase):
    def test_end_test_pass_updates_stats(self):
        self.printer.end_test(
            "uid-1", 0, 0, "Test 1", self._end_test_attrs("PASS", "Suite.Test 1")
        )
        self.assertEqual(len(self.stats.passed_tests), 1)
        self.assertEqual(len(self.stats.completed_tests), 1)

    def test_end_test_fail_updates_stats(self):
        self.printer.end_test(
            "uid-1", 0, 0, "Test 1", self._end_test_attrs("FAIL", "Suite.Test 1")
        )
        self.assertEqual(len(self.stats.failed_tests), 1)

    def test_end_test_adds_task_status_to_progress_box(self):
        self.printer.end_test(
            "uid-1", 0, 0, "Test 1", self._end_test_attrs("PASS", "Suite.Test 1")
        )
        self.assertIn("PASS", self.progress_box._task_statuses)

    def test_end_test_clears_executor_status(self):
        self.printer.end_test(
            "uid-1", 0, 0, "Test 1", self._end_test_attrs("PASS", "Suite.Test 1")
        )
        self.assertEqual(self.progress_box._executor_statuses[0], "[0][ 0]")


class TestStreamedTracePrinterLogMessages(TestStreamedTracePrinterBase):
    def test_log_warning_updates_stats(self):
        self.printer.start_test(
            "uid-1", 0, 0, "Test 1", self._test_attrs("Suite.Test 1")
        )
        self.printer.log_warning("uid-1", 0, 0, "A warning")
        self.assertEqual(len(self.stats.warnings), 1)

    def test_log_error_updates_stats(self):
        self.printer.start_test(
            "uid-1", 0, 0, "Test 1", self._test_attrs("Suite.Test 1")
        )
        self.printer.log_error("uid-1", 0, 0, "An error")
        self.assertEqual(len(self.stats.errors), 1)


class TestStreamedTracePrinterPrintTrace(TestStreamedTracePrinterBase):
    def test_print_trace_decodes_binary_and_calls_callback(self):
        binary_payload = MagicMock()
        binary_payload.data = b"Hello trace"
        self.printer.print_trace("uid-1", 0, 0, binary_payload)
        self.assertEqual(self.printed, ["Hello trace"])

    def test_print_trace_uses_console_lock(self):
        # Verify the lock is acquired (no deadlock or race on single thread)
        binary_payload = MagicMock()
        binary_payload.data = b"Safe"
        self.printer.print_trace("uid-1", 0, 0, binary_payload)
        self.assertFalse(self.printer.console_lock.locked())


# ---------------------------------------------------------------------------
# PabotTraceCollector
# ---------------------------------------------------------------------------


class TestPabotTraceCollectorInit(unittest.TestCase):
    def setUp(self):
        self.stream = StringIO()
        self.progress_box = MagicMock(spec=ProgressBox)
        self.collector = PabotTraceCollector(
            self.stream, process_count=4, progress_box=self.progress_box
        )

    def test_initial_process_count(self):
        self.assertEqual(self.collector.process_count, 4)

    def test_initial_print_summary_true(self):
        self.assertTrue(self.collector.print_summary)

    def test_initial_run_start_time_none(self):
        self.assertIsNone(self.collector.run_start_time)

    def test_initial_server_none(self):
        self.assertIsNone(self.collector.server)

    def test_initial_server_thread_none(self):
        self.assertIsNone(self.collector.server_thread)

    def test_init_draws_progress_box(self):
        self.progress_box.draw.assert_called_once()

    def test_stats_is_threaded_test_statistics(self):
        self.assertIsInstance(self.collector.stats, ThreadedTestStatistics)


class TestPabotTraceCollectorWriteln(unittest.TestCase):
    def setUp(self):
        self.stream = StringIO()
        self.progress_box = MagicMock(spec=ProgressBox)
        self.collector = PabotTraceCollector(
            self.stream, process_count=2, progress_box=self.progress_box
        )
        self.collector.stream = self.stream

    def test_writeln_writes_text_with_newline(self):
        self.collector._writeln("hello")
        self.assertEqual(self.stream.getvalue(), "hello\n")

    def test_writeln_empty_writes_only_newline(self):
        self.collector._writeln()
        self.assertEqual(self.stream.getvalue(), "\n")


class TestPabotTraceCollectorPrintTrace(unittest.TestCase):
    def setUp(self):
        self.stream = StringIO()
        self.progress_box = MagicMock(spec=ProgressBox)
        self.collector = PabotTraceCollector(
            self.stream, process_count=2, progress_box=self.progress_box
        )
        self.collector.stream = self.stream

    def test_print_trace_clears_progress_box(self):
        self.collector._print_trace("some trace")
        self.progress_box.clear.assert_called_once()

    def test_print_trace_writes_text(self):
        self.collector._print_trace("some trace")
        self.assertIn("some trace", self.stream.getvalue())

    def test_print_trace_redraws_progress_box(self):
        self.collector._print_trace("some trace")
        # draw() is called once at init, then again after printing trace
        self.assertEqual(self.progress_box.draw.call_count, 2)


class TestPabotTraceCollectorContextManager(unittest.TestCase):
    def setUp(self):
        self.progress_box = MagicMock(spec=ProgressBox)

        self.mock_server = MagicMock()
        self.mock_server.server_address = ("127.0.0.1", 1234)
        self.mock_thread = MagicMock()

        self.server_patcher = patch(
            "pabot_trace.PabotTraceCollector.ThreadedXMLRPCServer",
            return_value=self.mock_server,
        )
        self.thread_patcher = patch(
            "pabot_trace.PabotTraceCollector.threading.Thread",
            return_value=self.mock_thread,
        )
        self.mock_server_cls = self.server_patcher.start()
        self.mock_thread_cls = self.thread_patcher.start()

    def tearDown(self):
        self.server_patcher.stop()
        self.thread_patcher.stop()

    def _make_collector(self):
        collector = PabotTraceCollector(
            StringIO(), process_count=2, progress_box=self.progress_box
        )
        return collector

    def test_enter_sets_run_start_time(self):
        collector = self._make_collector()
        with collector:
            self.assertIsNotNone(collector.run_start_time)

    def test_enter_creates_server(self):
        collector = self._make_collector()
        with collector:
            self.mock_server_cls.assert_called_once()

    def test_enter_starts_server_thread(self):
        collector = self._make_collector()
        with collector:
            self.mock_thread.start.assert_called_once()

    def test_exit_shuts_down_server(self):
        collector = self._make_collector()
        with collector:
            pass
        self.mock_server.shutdown.assert_called_once()

    def test_exit_closes_server(self):
        collector = self._make_collector()
        with collector:
            pass
        self.mock_server.server_close.assert_called_once()

    def test_exit_joins_server_thread(self):
        collector = self._make_collector()
        with collector:
            pass
        self.mock_thread.join.assert_called_once()

    def test_exit_clears_progress_box(self):
        collector = self._make_collector()
        with collector:
            pass
        self.progress_box.clear.assert_called()

    def test_exit_registers_all_rpc_functions(self):
        collector = self._make_collector()
        with collector:
            pass
        registered_names = [
            c.args[1] for c in self.mock_server.register_function.call_args_list
        ]
        self.assertIn("report_test_count", registered_names)
        self.assertIn("report_context", registered_names)
        self.assertIn("start_suite", registered_names)
        self.assertIn("end_suite", registered_names)
        self.assertIn("start_test", registered_names)
        self.assertIn("end_test", registered_names)
        self.assertIn("log_warning", registered_names)
        self.assertIn("log_error", registered_names)
        self.assertIn("print_trace", registered_names)


class TestPabotTraceCollectorSummary(unittest.TestCase):
    def setUp(self):
        self.stream = StringIO()
        self.progress_box = MagicMock(spec=ProgressBox)

        self.mock_server = MagicMock()
        self.mock_thread = MagicMock()
        self.server_patcher = patch(
            "pabot_trace.PabotTraceCollector.ThreadedXMLRPCServer",
            return_value=self.mock_server,
        )
        self.thread_patcher = patch(
            "pabot_trace.PabotTraceCollector.threading.Thread",
            return_value=self.mock_thread,
        )
        self.server_patcher.start()
        self.thread_patcher.start()

    def tearDown(self):
        self.server_patcher.stop()
        self.thread_patcher.stop()

    def _run_collector(self, **kwargs):
        collector = PabotTraceCollector(
            self.stream, process_count=2, progress_box=self.progress_box
        )
        for k, v in kwargs.items():
            setattr(collector, k, v)
        with collector:
            pass
        return self.stream.getvalue()

    def test_exit_prints_run_complete_summary(self):
        output = self._run_collector()
        self.assertIn("RUN COMPLETE", output)

    def test_exit_no_summary_when_disabled(self):
        output = self._run_collector(print_summary=False)
        self.assertNotIn("RUN COMPLETE", output)

    def test_exit_prints_elapsed_time(self):
        output = self._run_collector()
        self.assertIn("Total elapsed:", output)

    def test_exit_elapsed_time_not_printed_when_quiet(self):
        from robot_trace.RobotTrace import Verbosity

        output = self._run_collector(verbosity=Verbosity.QUIET)
        self.assertNotIn("Total elapsed:", output)
