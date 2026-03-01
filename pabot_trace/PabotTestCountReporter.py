from xmlrpc.client import ServerProxy

HOST = "127.0.0.1"
PORT = 5292


class PabotTestCountReporter:
    def visit_suite(self, suite):
        # Connect to the collector server and report total test count.
        proxy = ServerProxy(f"http://{HOST}:{PORT}/", allow_none=True)
        proxy.report_test_count(suite.test_count)
