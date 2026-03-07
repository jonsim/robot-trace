# Alternative RobotFramework CLI Frontend

A lightweight Robot Framework CLI Frontend that provides real-time progress
updates directly on the command-line during test execution. The main design
intention is that you shouldn't need to open the HTML files directly to debug
failing tests - the information you need should be on the CLI, in as concise
and intuitive a format as possible.

## Features
- Provides a new `robot-trace` front-end, which is a drop-in replacement for
  `robot`.
- Provides a new `pabot-trace` front-end, which is a drop-in replacement for
  `pabot` (if you have it installed - there is no need to install this package
  if you don't).
- Provides a new `rebot-trace` command, which can be used to generate matching
  traces from an output.xml file.
- Displays test execution progress in the CLI.
- Provides a clear and concise overview of running tests.
- Provides a full, intuitive trace of any failing tests.
- Configurable output.

## Robot Usage
The listener supports three different usage models:

### 1. As a separate command-line tool
This is the easiest and recommended usage model.

#### Installation
```sh
pip install robotframework-trace
```

#### Usage
```sh
robot-trace path/to/tests
```

#### Details
You don't need to remember any extra arguments to pass to Robot - the runner
automatically passes the correct arguments to Robot and bases its own command
line from the arguments you pass to Robot. This gives a drop-in replacement
for any existing `robot` command lines.

The `robot-trace` command is a very thin wrapper on top of `robot` - it passes all
arguments it receives straight through, while adding additional arguments to
ensure the listener output works properly.

Robot's standard `--consolewidth` and `--consolecolors` arguments control the
listener's output; their behavior matches Robot's documentation.

`robot-trace` also introduces its own custom arguments that are consumed (matching
[Robot's argument parsing conventions](https://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#command-line-options)
regarding case insensitivity and hyphenation) before passing the command line to
Robot:
- `--verbose`: Sets the listener verbosity to `DEBUG` verbosity. Traces from all
  tests are printed.
- `--quiet`: Sets the listener verbosity to `QUIET` verbosity. Only traces from
  failing tests are printed. Passing tests that raise warnings or errors are
  not printed.
- `--consoleprogress <value>`: Controls where the progress box is printed.
  Valid values are `AUTO`, `STDOUT`, `STDERR`, `NONE` (to suppress it). Defaults
  to `AUTO`, which will print to `stdout` or `stderr` if they haven't been
  redirected, or suppress it otherwise.
- `--tracesubprocesses`: Traces all lines printed by subprocesses (e.g. via the
  _Run Process_ keyword) as 'TRACE' level messages. Note that this only emits
  them to the console log, not any of the output files.


### 2. As a module-based Robot listener
If you want to keep using `robot` directly, you can use the listener as a
module.

#### Installation
```sh
pip install robotframework-trace
```

#### Usage
When calling the listener directly, ensure you call Robot with `--console=none`
to avoid Robot's default console markers getting interleaved.
```sh
robot --listener robot_trace --console=none path/to/tests
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
- `trace_subprocesses=<value>`: Traces all lines printed by subprocesses (e.g.
  via the _Run Process_ keyword) as 'TRACE' level messages. Note that this only
  emits them to the console log, not any of the output files. Valid values are
  `True` or `False`. Defaults to `False`.
- `width=<value>`: Controls the width of the progress box. Defaults to `120`.


### 3. As a single-file Robot listener
If you don't want to install the package, the listener is implemented as a
single file which you can deploy standalone. This is useful for minimal setups
or for embedding the listener in your own projects, but you lose the ability to
update via `pip`.

#### Installation
Copy `robot_trace/RobotTrace.py` to your project directory.

#### Usage
Usage is identical to option 2, except using the file not the module:
```sh
robot --listener RobotTrace.py --console=none path/to/tests
```


### Related options
You may also consider calling `robot` or `robot-trace` with:
- `--maxerrorlines=10000` to avoid truncating all but the longest error
  messages.
- `--maxassignlength=10000` to avoid truncating all but the longest variables.


### Example Output
![](https://raw.githubusercontent.com/jonsim/robot-trace/main/robot_trace_demo.gif)



## Pabot Usage
For `pabot`, due to the complexity of the tool and the lack of comprehensive
API entrypoints, the listener supports a single usage model:

### As a separate command-line tool
#### Installation
```sh
pip install robotframework-trace
```

#### Usage
```sh
pabot-trace path/to/tests
```

#### Details
You don't need to remember any extra arguments to pass to pabot - the runner
automatically passes the correct arguments to pabot and bases its own command
line from the arguments you pass to pabot. This gives a drop-in replacement
for any existing `pabot` command lines.

The `pabot-trace` command is a thin wrapper on top of `pabot` - it passes all
arguments it receives straight through, while adding additional arguments to
ensure the listener output works properly.

All arguments match those of `robot-trace` - see the [Robot Usage](#robot-usage)
section for details.


### Example Output
![](https://raw.githubusercontent.com/jonsim/robot-trace/main/pabot_trace_demo.gif)



## Rebot Usage
A separate `rebot-trace` application is also provided. Despite its name, it is
not a wrapper around `rebot`, but rather a separate application that can be used
to process Robot Framework result files (in a similar manner to `rebot`). Thus
there is a single usage model:

### As a separate command-line tool
#### Installation
```sh
pip install robotframework-trace
```

#### Usage
```sh
rebot-trace path/to/output.xml
```

#### Details
`rebot-trace` supports the following command line arguments:
- `--verbose`: Sets the listener verbosity to `DEBUG` verbosity. Traces from all
  tests are printed (matching `robot-trace` behavior).
- `--quiet`: Sets the listener verbosity to `QUIET` verbosity. Only traces from
  failing tests are printed. Passing tests that raise warnings or errors are
  not printed (matching `robot-trace` behavior).

The traces output are identical to those output by `robot-trace` and
`pabot-trace`, with the following exceptions:
- Any messages logged to the console are not output.
- The `--trace-subprocesses` argument is unsupported.


### Example Output
![](https://raw.githubusercontent.com/jonsim/robot-trace/main/rebot_trace_demo.gif)



### Redirected Output
You can also redirect the output to a file to get the same output without the
live progress reporting:
```sh
$ robot-trace tests/example | cat
TEST FAILED: Example.Nested Keywords Failing.Nested Failing Test Case
═════════════════════════════════════════════════════════════════════
▶ Level One Keyword()
  ▶ BuiltIn.Log('In the level one keyword')
    I In the level one keyword
    ✓ PASS     0s
  ▶ Level Two Keyword()
    ▶ BuiltIn.Log('In the level two keyword')
      I In the level two keyword
      ✓ PASS     0s
    ▶ Level Three Keyword()
      ▶ BuiltIn.Log('In the level three keyword')
        I In the level three keyword
        ✓ PASS     0s
      ▶ BuiltIn.Fail('This keyword failed')
        F This keyword failed
        ✗ FAIL     0s
      ✗ FAIL     0s
    ✗ FAIL     0s
  ✗ FAIL     0s

RUN COMPLETE: 14 tests, 14 completed (13 passed, 0 skipped, 1 failed).

Failing test:
- Example.Nested Keywords Failing.Nested Failing Test Case

Total elapsed:  5s.
```

## Requirements
- Python 3.6+
- Robot Framework 5.0+
- (Optional) pabot 5.0+

The script has no dependencies beyond the standard library. On Windows to get
colorized output, you need to install the `colorama` package, however the script
will work without it.

The script has no direct dependency on `robotframework` itself, but obviously it
doesn't do much without it installed.


## Contributing
Contributions, bugs, and feature requests are welcome! Please see the
[Contributing Guide](CONTRIBUTING.md) for details on how to build the project
locally and submit changes.


## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file
for details.
