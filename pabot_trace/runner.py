#
# A wrapper around pabot that starts a collector server and invokes all robot
# sub-processes with a custom listener to report back to the collector. This
# file is provided under the MIT license.
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
import subprocess
import sys

from robot_trace.RobotTrace import RobotTraceArgs
from robot_trace.runner import RobotTraceRunnerArgs

from .PabotTraceCollector import ExecutorProgressBox, PabotTraceCollector


def main():
    # Parse arguments for the runner wrapper.
    args = RobotTraceRunnerArgs(sys.argv[1:])

    # Build the command to run robot.
    listener = "pabot_trace"
    listener_kwargs = {}
    if args.verbosity is not None:
        listener += f":verbosity={args.verbosity}"
        listener_kwargs["verbosity"] = str(args.verbosity)
    if args.console_colors is not None:
        listener += f":colors={args.console_colors}"
        listener_kwargs["colors"] = str(args.console_colors)
    if args.console_progress is not None:
        listener_kwargs["console_progress"] = str(args.console_progress)
    if args.trace_subprocesses:
        listener += ":trace_subprocesses=True"
        listener_kwargs["trace_subprocesses"] = True
    if args.console_width is not None:
        listener += f":width={args.console_width}"
        listener_kwargs["width"] = int(args.console_width)
    cmd = [
        "pabot",
        "--pabotprerunmodifier",
        "pabot_trace.PabotTestCountReporter",
        "--pabotconsole",
        "none",
        "--console=quiet",
        "--listener",
        listener,
        *args.robot_args,
    ]

    # Determine the number of processes to use.
    try:
        import pabot.arguments

        args, pabot_args = pabot.arguments._parse_pabot_args(cmd)
        processes = int(pabot_args["processes"])
    except Exception:
        import multiprocessing

        processes = max(2, multiprocessing.cpu_count())

    # Pabot doesn't have the concept of a 'top level listener', so we implement
    # our own equivalent in this wrapper. Parse the arguments to determine the
    # console colors and width.
    listener_args = RobotTraceArgs(**listener_kwargs)

    # Create the reporting mechanism.
    progress_box = ExecutorProgressBox(
        listener_args.progress_stream,
        processes,
        listener_args.colors,
        listener_args.width,
    )

    # Start the collector server.
    try:
        with PabotTraceCollector(sys.stdout, processes, progress_box) as collector:
            result = subprocess.run(cmd, capture_output=True)
            # Pabot returns 253 if you pass useful arguments like `--no-rebot`,
            # so basically ignore the 253 return code. Sadly this return code
            # also overrides everything else, meaning you lose a programmatic
            # way of telling if the tests failed.
            if result.returncode != 253 and result.returncode > 250:
                collector.print_summary = False
        # If the process failed because of an internal error (likely when
        # parsing arguments or in the listener itself), print the error message.
        if result.returncode > 250:
            sys.stdout.write(result.stdout.decode())
            sys.stderr.write(result.stderr.decode())
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        sys.exit(130)
