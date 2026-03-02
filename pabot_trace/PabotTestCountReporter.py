#
# A Robot prerunmodifier which simply visits the top-level suite, records the
# total test count, and reports it back to a top-level collector
# (PabotTraceCollector).
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
import os
from xmlrpc.client import ServerProxy

HOST = "127.0.0.1"


class PabotTestCountReporter:
    """
    A Robot Framework prerun modifier that reports the total test count to the
    PabotTraceCollector.
    """

    def visit_suite(self, suite):
        """
        Visits the test suite and reports its total test count to the collector.
        Does not visit any child suites or tests.
        """
        # Connect to the collector server and report total test count.
        port = int(os.environ["_PABOT_TRACE_COLLECTOR_PORT"])
        proxy = ServerProxy(f"http://{HOST}:{port}/", allow_none=True)
        proxy.report_test_count(suite.test_count)
