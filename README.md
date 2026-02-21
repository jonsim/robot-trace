# RobotFramework CLI Progress Listener

A lightweight Robot Framework listener that provides real-time progress updates
directly on the command-line during test execution. The main design intention is
you don't need to open the HTML files directly to debug failing tests.

## Features
- Displays test execution progress in the CLI.
- Provides a clear and concise overview of running tests.
- Provides a full, intuitive trace of any failing tests.

## Usage
The listener supports three different usage models:

### 1. As a separate command-line tool
This is the easiest and recommended usage model.

#### Installation
```sh
pip install robotframework-cliprogress
```

#### Usage
```sh
robot-cli path/to/tests
```

#### Details
You don't need to remember any extra arguments to pass to Robot - the runner
automatically passes the correct arguments to Robot and bases its own command
line from the arguments you pass to Robot. This gives a drop-in replacement
for any existing `robot` command lines.

The `robot-cli` command is a very thin wrapper on top of `robot` - it passes all
arguments it receives straight through, while adding additional arguments to
ensure the listener output works properly.

Robot's standard `--consolewidth` and `--consolecolors` arguments control the
listener's output; their behavior matches Robot's documentation.

`robot-cli` also introduces its own custom arguments that are consumed (matching
Robot's argument parsing conventions regarding case insensitivity and
hyphenation) before passing the command line to Robot:
- `--verbose`: Sets the listener verbosity to `DEBUG` verbosity. Traces from all
  tests are printed.
- `--quiet`: Sets the listener verbosity to `QUIET` verbosity. Only traces from
  failing tests are printed. Passing tests that raise warnings or errors are
  not printed.
- `--consoleprogress <value>`: Controls where the progress box is printed.
  Valid values are `AUTO`, `STDOUT`, `STDERR`, `NONE` (to suppress it). Defaults
  to `AUTO`, which will print to `stdout` or `stderr` if they haven't been
  redirected, or suppress it otherwise.


### 2. As a module-based Robot listener
If you want to keep using `robot` directly, you can use the listener as a
module.

#### Installation
```sh
pip install robotframework-cliprogress
```

#### Usage
When calling the listener directly, ensure you call Robot with `--console=none`
to avoid Robot's default console markers getting interleaved.
```sh
robot --listener CLIProgress --console=none path/to/tests
```

#### Details
The listener supports the following arguments:
- `verbosity=<value>`: takes a string value to set the listener's verbosity.
  Valid values are `DEBUG` (print traces from all tests), `NORMAL` (print traces
  from failing, warning, and erroring tests), `QUIET` (print traces from failing
  tests). Defaults to `NORMAL`.
- `colors=<value>`: takes a string value to control whether or not the output is
  colorized. Valid values are `AUTO`, `ON`, `ANSI`, `OFF`. Values behave the same
  as Robot's `--consolecolors` argument. Defaults to `AUTO`.
- `console_progress=<value>`: Controls where the progress box is printed. Valid
  values are `AUTO`, `STDOUT`, `STDERR`, `NONE` (to suppress it). Defaults to
  `AUTO`, which will print to `stdout` or `stderr` if they haven't been
  redirected, or suppress it otherwise.
- `width=<value>`: Controls the width of the progress box. Defaults to `120`.


### 3. As a single-file Robot listener
If you don't want to install the package, the listener is implemented as a
single file which you can deploy standalone. This is useful for minimal setups
or for embedding the listener in your own projects, but you lose the ability to
update via `pip`.

#### Installation
Copy `CLIProgress/CLIProgress.py` to your project directory.

#### Usage
Usage is identical to option 2, except using the file not the module:
```sh
robot --listener CLIProgress.py --console=none path/to/tests
```


### Related options
You may also consider calling `robot` or `robot-cli` with:
- `--maxerrorlines=10000` to avoid truncating all but the longest error
  messages.
- `--maxassignlength=10000` to avoid truncating all but the longest variables.


## Example Output
```sh
$ robot-cli testcases
TEST FAILED: Nested Keywords.Nested Failing Test Case
═════════════════════════════════════════════════════
▶ Level Two Keyword('should_fail=${True}')
  ▶ BuiltIn.Log('In the level two keyword')
    I In the level two keyword
    ✓ PASS     0s
  ▶ Level Three Keyword()
    ▶ BuiltIn.Log('In the level three keyword')
      I In the level three keyword
      ✓ PASS     0s
    ✓ PASS     0s
  ▶ Failing Keyword()
    ▶ BuiltIn.Log('In the failing keyword')
      I In the failing keyword
      ✓ PASS     0s
    ▶ BuiltIn.Fail('This keyword failed')
      F This keyword failed
      ✗ FAIL     0s
    ✗ FAIL     0s
  ✗ FAIL     0s

┌──────────────────────────────────────────────────────────────────────┐
│ [SUITE  2/ 2] Suite 2                                                │
│ [TEST 11/16] Test Case 3 - Slow               (elapsed  4s, ETA  3s) │
│ [Sleep]  '${DELAY_LONG}'                                             │
└──────────────────────────────────────────────────────────────────────┘
```

## Requirements
- Python 3.6+
- Robot Framework 4.0+

The script has no dependencies beyond the standard library. On Windows to get
colorized output, you need to install the `colorama` package, however the script
will work without it.


## Contributing
Contributions, bugs, and feature requests are welcome! Please see the
[Contributing Guide](CONTRIBUTING.md) for details on how to build the project
locally and submit changes.


## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file
for details.
