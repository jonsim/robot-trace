# Unit tests for robot_trace/runner.py.
#
# Copyright (c) 2026 Jonathan Simmonds
import unittest

from robot_trace.runner import RobotTraceRunnerArgs


def make(*args: str) -> RobotTraceRunnerArgs:
    """Convenience helper: build RobotTraceRunnerArgs from positional strings."""
    return RobotTraceRunnerArgs(list(args))


class TestRobotTraceRunnerArgsDefaults(unittest.TestCase):
    """All fields should have sensible defaults on an empty arg list."""

    def setUp(self):
        self.args = make()

    def test_robot_args_empty(self):
        self.assertEqual(self.args.robot_args, [])

    def test_console_colors_none(self):
        self.assertIsNone(self.args.console_colors)

    def test_console_width_none(self):
        self.assertIsNone(self.args.console_width)

    def test_console_progress_none(self):
        self.assertIsNone(self.args.console_progress)

    def test_trace_subprocesses_false(self):
        self.assertFalse(self.args.trace_subprocesses)

    def test_verbosity_none(self):
        self.assertIsNone(self.args.verbosity)


class TestRobotTraceRunnerArgsConsoleColors(unittest.TestCase):
    """--consolecolors / -C parsing."""

    def test_long_space_separator(self):
        args = make("--consolecolors", "ON")
        self.assertEqual(args.console_colors, "ON")

    def test_long_equals_separator(self):
        args = make("--consolecolors=ON")
        self.assertEqual(args.console_colors, "ON")

    def test_long_case_insensitive(self):
        args = make("--ConsoleColors", "ANSI")
        self.assertEqual(args.console_colors, "ANSI")

    def test_long_hyphen_insensitive(self):
        args = make("--console-colors", "OFF")
        self.assertEqual(args.console_colors, "OFF")

    def test_short_space_separator(self):
        args = make("-C", "OFF")
        self.assertEqual(args.console_colors, "OFF")

    def test_short_inline_value(self):
        args = make("-CANSI")
        self.assertEqual(args.console_colors, "ANSI")

    def test_repeated_last_wins(self):
        args = make("--consolecolors", "ON", "--consolecolors", "OFF")
        self.assertEqual(args.console_colors, "OFF")

    def test_passthrough_long_space(self):
        """--consolecolors and its value must be passed through to robot_args."""
        args = make("--consolecolors", "ON")
        self.assertIn("--consolecolors", args.robot_args)
        self.assertIn("ON", args.robot_args)

    def test_passthrough_long_equals(self):
        args = make("--consolecolors=ON")
        self.assertIn("--consolecolors=ON", args.robot_args)

    def test_passthrough_short_inline(self):
        args = make("-CANSI")
        self.assertIn("-CANSI", args.robot_args)


class TestRobotTraceRunnerArgsConsoleWidth(unittest.TestCase):
    """--consolewidth / -W parsing."""

    def test_long_space_separator(self):
        args = make("--consolewidth", "120")
        self.assertEqual(args.console_width, "120")

    def test_long_equals_separator(self):
        args = make("--consolewidth=80")
        self.assertEqual(args.console_width, "80")

    def test_long_hyphen_insensitive(self):
        args = make("--console-width", "100")
        self.assertEqual(args.console_width, "100")

    def test_short_space_separator(self):
        args = make("-W", "100")
        self.assertEqual(args.console_width, "100")

    def test_short_inline_value(self):
        args = make("-W100")
        self.assertEqual(args.console_width, "100")

    def test_repeated_last_wins(self):
        args = make("-W", "80", "-W", "120")
        self.assertEqual(args.console_width, "120")

    def test_passthrough_long_space(self):
        args = make("--consolewidth", "80")
        self.assertIn("--consolewidth", args.robot_args)
        self.assertIn("80", args.robot_args)

    def test_passthrough_short(self):
        args = make("-W", "80")
        self.assertIn("-W", args.robot_args)
        self.assertIn("80", args.robot_args)


class TestRobotTraceRunnerArgsConsoleProgress(unittest.TestCase):
    """--consoleprogress is a custom arg: captured but NOT passed through."""

    def test_long_space_separator(self):
        args = make("--consoleprogress", "STDOUT")
        self.assertEqual(args.console_progress, "STDOUT")

    def test_long_equals_separator(self):
        args = make("--consoleprogress=STDERR")
        self.assertEqual(args.console_progress, "STDERR")

    def test_long_hyphen_insensitive(self):
        args = make("--console-progress", "NONE")
        self.assertEqual(args.console_progress, "NONE")

    def test_long_case_insensitive(self):
        args = make("--ConsoleProgress", "AUTO")
        self.assertEqual(args.console_progress, "AUTO")

    def test_stripped_from_robot_args_space(self):
        args = make("--consoleprogress", "STDOUT")
        self.assertNotIn("--consoleprogress", args.robot_args)
        self.assertNotIn("STDOUT", args.robot_args)

    def test_stripped_from_robot_args_equals(self):
        args = make("--consoleprogress=STDOUT")
        self.assertNotIn("--consoleprogress=STDOUT", args.robot_args)


class TestRobotTraceRunnerArgsTraceSubprocesses(unittest.TestCase):
    """--tracesubprocesses is a flag (no value) that is stripped from robot_args."""

    def test_sets_flag(self):
        args = make("--tracesubprocesses")
        self.assertTrue(args.trace_subprocesses)

    def test_hyphen_insensitive(self):
        args = make("--trace-subprocesses")
        self.assertTrue(args.trace_subprocesses)

    def test_case_insensitive(self):
        args = make("--TraceSubprocesses")
        self.assertTrue(args.trace_subprocesses)

    def test_stripped_from_robot_args(self):
        args = make("--tracesubprocesses")
        self.assertNotIn("--tracesubprocesses", args.robot_args)


class TestRobotTraceRunnerArgsVerbosity(unittest.TestCase):
    """--verbose and --quiet are custom flags stripped from robot_args."""

    def test_verbose_sets_debug(self):
        args = make("--verbose")
        self.assertEqual(args.verbosity, "DEBUG")

    def test_quiet_sets_quiet(self):
        args = make("--quiet")
        self.assertEqual(args.verbosity, "QUIET")

    def test_verbose_case_insensitive(self):
        args = make("--VERBOSE")
        self.assertEqual(args.verbosity, "DEBUG")

    def test_quiet_case_insensitive(self):
        args = make("--QUIET")
        self.assertEqual(args.verbosity, "QUIET")

    def test_verbose_stripped_from_robot_args(self):
        args = make("--verbose")
        self.assertNotIn("--verbose", args.robot_args)

    def test_quiet_stripped_from_robot_args(self):
        args = make("--quiet")
        self.assertNotIn("--quiet", args.robot_args)

    def test_repeated_last_wins_quiet_then_verbose(self):
        args = make("--quiet", "--verbose")
        self.assertEqual(args.verbosity, "DEBUG")

    def test_repeated_last_wins_verbose_then_quiet(self):
        args = make("--verbose", "--quiet")
        self.assertEqual(args.verbosity, "QUIET")


class TestRobotTraceRunnerArgsPassthrough(unittest.TestCase):
    """Unrecognised arguments must be forwarded verbatim in robot_args."""

    def test_positional_arg(self):
        args = make("tests/")
        self.assertIn("tests/", args.robot_args)

    def test_unknown_long_option_space(self):
        args = make("--include", "smoke")
        self.assertEqual(args.robot_args, ["--include", "smoke"])

    def test_unknown_long_option_equals(self):
        args = make("--include=smoke")
        self.assertEqual(args.robot_args, ["--include=smoke"])

    def test_unknown_short_option_inline(self):
        args = make("-ismoke")
        self.assertEqual(args.robot_args, ["-ismoke"])

    def test_order_preserved(self):
        args = make("--include", "smoke", "tests/", "--dryrun")
        self.assertEqual(args.robot_args, ["--include", "smoke", "tests/", "--dryrun"])


class TestRobotTraceRunnerArgsMixed(unittest.TestCase):
    """Realistic combined command lines."""

    def test_custom_args_stripped_passthrough_kept(self):
        args = make(
            "--verbose",
            "--consoleprogress",
            "STDERR",
            "--consolecolors",
            "ON",
            "--include",
            "smoke",
            "tests/",
        )
        self.assertEqual(args.verbosity, "DEBUG")
        self.assertEqual(args.console_progress, "STDERR")
        self.assertEqual(args.console_colors, "ON")
        # Custom args must not bleed into robot_args.
        self.assertNotIn("--verbose", args.robot_args)
        self.assertNotIn("--consoleprogress", args.robot_args)
        self.assertNotIn("STDERR", args.robot_args)
        # Passthrough args must be present and in order.
        self.assertEqual(
            args.robot_args,
            ["--consolecolors", "ON", "--include", "smoke", "tests/"],
        )

    def test_tracesubprocesses_with_other_args(self):
        args = make("--tracesubprocesses", "--consolewidth=80", "tests/suite.robot")
        self.assertTrue(args.trace_subprocesses)
        self.assertEqual(args.console_width, "80")
        self.assertNotIn("--tracesubprocesses", args.robot_args)
        self.assertIn("--consolewidth=80", args.robot_args)
        self.assertIn("tests/suite.robot", args.robot_args)

    def test_missing_value_for_consoleprogress_at_end(self):
        """If --consoleprogress appears as the last arg with no value, it should
        be captured with None and not crash."""
        args = make("--consoleprogress")
        self.assertIsNone(args.console_progress)
        self.assertNotIn("--consoleprogress", args.robot_args)
