import os
from xmlrpc.client import ServerProxy

HOST = "127.0.0.1"


class PabotTestCountReporter:
    def visit_suite(self, suite):
        # Connect to the collector server and report total test count.
        port = int(os.environ["_PABOT_TRACE_COLLECTOR_PORT"])
        proxy = ServerProxy(f"http://{HOST}:{port}/", allow_none=True)
        proxy.report_test_count(suite.test_count)
