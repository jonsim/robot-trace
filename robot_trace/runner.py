#
# A thin wrapper around robot that adds the RobotTrace listener and
# automatically sets its arguments. This file is provided under the MIT license.
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


def main():
    args = sys.argv[1:]

    # Normalize arguments to match Robot's argument handling, as documented by:
    # https://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#using-command-line-options
    # Specifically, we implement the following rules:
    # - Long options are case-insensitive and hyphen-insensitive.
    # - Option calues are separated by a space (`--include tag`, `-i tag`),
    #   equals (`--include=tag`), or no separator for short (`-itag`).
    # - Repeated single-value options: last value wins.
    # - Repeated multi-value options: values are appended.
    # We ignore the following rules:
    # - Long options can be abbreviated if unique (e.g., --logle → --loglevel)
    #   - This would require hardcoding far too much about Robot's arguments.
    # We split all options up and normalize their names to make them easier to
    # parse. We don't modify these values and we _only_ use them for parsing in
    # this script - that way even if we screw something up in our parsing. We
    # pass through the original arg list.
    # We interpret some of Robot's built in arguments so that command lines work
    # as expected. These are:
    # - --consolecolors <value>, -C <value>
    # - --consolewidth <value>, -W <value>
    # We also define our own custom arguments. We remove these from the arg
    # list, so that they don't get passed through to Robot. These custom
    # arguments are:
    # - --consoleprogress <value>
    # - --verbose
    # - --quiet
    robot_args = []
    console_colors = None
    console_width = None
    console_progress = None
    trace_subprocesses = False
    verbosity = None

    arg_iter = iter(args)
    for arg in arg_iter:
        # Normalize argument to determine its name and potential inline value.
        if arg.startswith("--"):
            parts = arg.split("=", 1)
            name = "--" + parts[0][2:].lower().replace("-", "")
            value = parts[1] if len(parts) > 1 else None
        elif arg.startswith("-") and len(arg) > 2 and arg[1] != "-":
            name = arg[:2]
            value = arg[2:]
        else:
            name = arg
            value = None

        # Extract value from the next argument if needed and not inline.
        needs_value = name in {
            "-C",
            "--consolecolors",
            "-W",
            "--consolewidth",
            "--consoleprogress",
        }
        consumed_next = False
        if needs_value and value is None:
            try:
                value = next(arg_iter)
                consumed_next = True
            except StopIteration:
                pass

        # Capture specific arguments.
        if name in {"-C", "--consolecolors"}:
            console_colors = value
        elif name in {"-W", "--consolewidth"}:
            console_width = value
        elif name == "--consoleprogress":
            console_progress = value
        elif name == "--tracesubprocesses":
            trace_subprocesses = True
        elif name == "--verbose":
            verbosity = "DEBUG"
        elif name == "--quiet":
            verbosity = "QUIET"

        # Reconstruct robot_args, omitting our custom arguments.
        if name not in {
            "--consoleprogress",
            "--verbose",
            "--quiet",
            "--tracesubprocesses",
        }:
            robot_args.append(arg)
            if consumed_next and value is not None:
                robot_args.append(value)

    # Build the command to run robot.
    listener = "robot_trace"
    if console_colors is not None:
        listener += f":colors={console_colors}"
    if console_width is not None:
        listener += f":width={console_width}"
    if console_progress is not None:
        listener += f":console_progress={console_progress}"
    if trace_subprocesses:
        listener += ":trace_subprocesses=True"
    if verbosity is not None:
        listener += f":verbosity={verbosity}"
    cmd = [
        "robot",
        "--console=quiet",
        "--listener",
        listener,
        *robot_args,
    ]

    try:
        result = subprocess.run(cmd, stderr=subprocess.PIPE)
        # If the process failed because of an internal error (likely when
        # parsing arguments or in the listener itself), print the error message.
        if result.returncode > 250:
            sys.stderr.write(result.stderr.decode())
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        sys.exit(130)
