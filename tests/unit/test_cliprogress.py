import unittest
from unittest.mock import MagicMock, patch

from CLIProgress.CLIProgress import (
    ANSI,
    CLIProgress,
    TestStatistics,
    TestTimings,
    TraceStack,
    Verbosity,
    _ANSICode,
)


class TestVerbosity(unittest.TestCase):
    def test_equality(self):
        self.assertEqual(Verbosity.QUIET, Verbosity.QUIET)

    def test_inequality(self):
        self.assertNotEqual(Verbosity.QUIET, Verbosity.NORMAL)

    def test_ordering_less_than(self):
        self.assertLess(Verbosity.QUIET, Verbosity.NORMAL)

    def test_ordering_less_than_debug(self):
        self.assertLess(Verbosity.NORMAL, Verbosity.DEBUG)

    def test_from_string_lowercase(self):
        self.assertEqual(Verbosity.from_string("quiet"), Verbosity.QUIET)

    def test_from_string_uppercase(self):
        self.assertEqual(Verbosity.from_string("NORMAL"), Verbosity.NORMAL)

    def test_from_string_mixed_case(self):
        self.assertEqual(Verbosity.from_string("DeBuG"), Verbosity.DEBUG)

    def test_from_string_invalid(self):
        self.assertEqual(Verbosity.from_string("invalid"), Verbosity.NORMAL)


class TestANSI(unittest.TestCase):
    def test_ansicode_call(self):
        code = _ANSICode("\033[31m")
        result = code("Hello")
        self.assertEqual(result, "\033[31mHello\033[0m")

    def test_ansi_len(self):
        text = "Hello \033[31mWorld\033[0m!"
        self.assertEqual(ANSI.len(text), 12)  # "Hello World!"


class TestTraceStack(unittest.TestCase):
    def test_initial_state_trace(self):
        stack = TraceStack()
        self.assertEqual(stack.trace, "")

    def test_initial_state_errors(self):
        stack = TraceStack()
        self.assertFalse(stack.has_errors)

    def test_initial_state_warnings(self):
        stack = TraceStack()
        self.assertFalse(stack.has_warnings)

    def test_push_keyword(self):
        stack = TraceStack()
        stack.push_keyword("Keyword A")
        self.assertEqual(stack._depth, 1)

    def test_pop_keyword(self):
        stack = TraceStack()
        stack.push_keyword("Keyword A")
        stack.pop_keyword()
        self.assertEqual(stack._depth, 0)

    def test_flush_keyword_depth(self):
        stack = TraceStack()
        stack.push_keyword("Keyword A")
        stack.flush()
        self.assertEqual(stack._depth, 0)

    def test_flush_keyword_trace_content(self):
        stack = TraceStack()
        stack.push_keyword("Keyword A")
        stack.flush()
        self.assertIn("Keyword A", stack.trace)


class TestTestStatistics(unittest.TestCase):
    def test_start_suite_counts(self):
        stats = TestStatistics()
        suite_mock = MagicMock()
        suite_mock.suites = [1, 2, 3]
        suite_mock.test_count = 10

        stats.start_suite(suite_mock)
        self.assertEqual(stats.top_level_suite_count, 3)
        self.assertEqual(stats.top_level_test_count, 10)

    def test_start_test_increment(self):
        stats = TestStatistics()
        stats.start_test()
        self.assertEqual(stats.started_tests, 1)

    def test_end_test_pass(self):
        stats = TestStatistics()
        result_mock = MagicMock()
        result_mock.not_run = False
        result_mock.status = "PASS"

        stats.end_test(result_mock)
        self.assertEqual(stats.completed_tests, 1)
        self.assertEqual(stats.passed_tests, 1)

    def test_end_test_fail(self):
        stats = TestStatistics()
        result_mock = MagicMock()
        result_mock.not_run = False
        result_mock.status = "FAIL"

        stats.end_test(result_mock)
        self.assertEqual(stats.completed_tests, 1)
        self.assertEqual(stats.failed_tests, 1)


class TestTestTimings(unittest.TestCase):
    def test_format_time_none(self):
        self.assertEqual(TestTimings.format_time(None), "unknown")

    def test_format_time_seconds_only(self):
        self.assertEqual(TestTimings.format_time(45), "45s")

    def test_format_time_minutes_seconds(self):
        self.assertEqual(TestTimings.format_time(125), " 2m  5s")

    def test_format_time_hours_minutes_seconds(self):
        self.assertEqual(TestTimings.format_time(3665), " 1h  1m  5s")

    @patch("time.time", return_value=100.0)
    def test_elapsed_time(self, mock_time):
        timings = TestTimings()
        timings.start_suite()
        mock_time.return_value = 110.0
        self.assertEqual(timings.get_elapsed_time(), 10.0)


class TestCLIProgressHelper(unittest.TestCase):
    def setUp(self):
        self.cli = CLIProgress(verbosity="NORMAL", console_progress="NONE")

    def test_past_tense_upper_pass(self):
        self.assertEqual(self.cli._past_tense("PASS"), "PASSED")

    def test_past_tense_upper_fail(self):
        self.assertEqual(self.cli._past_tense("FAIL"), "FAILED")

    def test_past_tense_upper_skip(self):
        self.assertEqual(self.cli._past_tense("SKIP"), "SKIPPED")

    def test_past_tense_lower(self):
        self.assertEqual(self.cli._past_tense("pass"), "passed")

    def test_past_tense_title_try(self):
        self.assertEqual(self.cli._past_tense("Try"), "Tried")

    def test_past_tense_title_stop(self):
        self.assertEqual(self.cli._past_tense("Stop"), "Stopped")

    def test_verbosity_settings_debug(self):
        cli = CLIProgress(verbosity="DEBUG", console_progress="NONE")
        self.assertTrue(cli.print_passed)
        self.assertTrue(cli.print_skipped)
        self.assertTrue(cli.print_failed)

    def test_verbosity_settings_quiet(self):
        cli_quiet = CLIProgress(verbosity="QUIET", console_progress="NONE")
        self.assertFalse(cli_quiet.print_passed)
        self.assertTrue(cli_quiet.print_failed)


if __name__ == "__main__":
    unittest.main()
