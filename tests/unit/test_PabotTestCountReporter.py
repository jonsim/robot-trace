import unittest
from unittest.mock import MagicMock, patch

from pabot_trace.PabotTestCountReporter import PabotTestCountReporter


class TestPabotTestCountReporterVisitSuite(unittest.TestCase):
    def setUp(self):
        self.reporter = PabotTestCountReporter()

        self.mock_proxy = MagicMock()
        self.proxy_patcher = patch(
            "pabot_trace.PabotTestCountReporter.ServerProxy",
            return_value=self.mock_proxy,
        )
        self.proxy_patcher.start()

    def tearDown(self):
        self.proxy_patcher.stop()

    def _make_suite(self, test_count):
        suite = MagicMock()
        suite.test_count = test_count
        return suite

    def test_visit_suite_calls_report_test_count(self):
        suite = self._make_suite(10)
        self.reporter.visit_suite(suite)
        self.mock_proxy.report_test_count.assert_called_once_with(10)

    def test_visit_suite_reports_zero_tests(self):
        suite = self._make_suite(0)
        self.reporter.visit_suite(suite)
        self.mock_proxy.report_test_count.assert_called_once_with(0)

    def test_visit_suite_reports_large_count(self):
        suite = self._make_suite(9999)
        self.reporter.visit_suite(suite)
        self.mock_proxy.report_test_count.assert_called_once_with(9999)

    def test_visit_suite_creates_proxy_to_correct_host_port(self):
        from pabot_trace.PabotTestCountReporter import HOST, PORT

        suite = self._make_suite(1)
        with patch(
            "pabot_trace.PabotTestCountReporter.ServerProxy",
            return_value=self.mock_proxy,
        ) as mock_cls:
            self.reporter.visit_suite(suite)
            mock_cls.assert_called_once_with(f"http://{HOST}:{PORT}/", allow_none=True)

    def test_visit_suite_called_multiple_times_creates_new_proxy_each_time(self):
        suite = self._make_suite(5)
        with patch(
            "pabot_trace.PabotTestCountReporter.ServerProxy",
            return_value=self.mock_proxy,
        ) as mock_cls:
            self.reporter.visit_suite(suite)
            self.reporter.visit_suite(suite)
            self.assertEqual(mock_cls.call_count, 2)
