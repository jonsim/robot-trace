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

from robot.api import ExecutionResult

from robot_trace.RobotTrace import RobotTraceArgs

from .RebotTrace import RebotTrace, ResultVisitorListenerAdapter


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
