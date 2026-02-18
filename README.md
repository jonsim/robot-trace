# RobotFramework CLI Progress Listener

A lightweight Robot Framework listener that provides real-time progress updates
directly on the command-line during test execution. The main design intention is
you don't need to open the HTML files directly to debug failing tests.

**Note:** This is still very much a WIP.

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


### 2. As a module-based Robot listener
If you want to keep using `robot` directly, you can use the listener as a
module.

#### Installation
```sh
pip install robotframework-cliprogress
```

#### Usage
When calling the listener directly, it's recommended to also call with:
`--console=quiet` to avoid Robot's default console markers getting interleaved.
```sh
robot --listener CLIProgress --console=quiet path/to/tests
```

### 3. As a single-file Robot listener
If you don't want to install the package, the listener is implemented as a
single file which you can download separately. This is useful for minimal setups
or for embedding the listener in your own projects, but you lose the ability to
update via `pip`.

#### Installation
Copy `CLIProgress/CLIProgress.py` to your project directory.

#### Usage
Usage is broadly similar to option 2 - pass the file to Robot's `--listener`
argument, and also pass `--console=quiet` to avoid Robot's default console
markers getting interleaved.
```sh
robot --listener CLIProgress.py --console=quiet path/to/tests
```

### Related options
You may also consider calling `robot` or `robot-cli` with:
- `--maxerrorlines=10000` to avoid truncating all but the longest error
  messages.
- `--maxassignlength=10000` to avoid truncating all but the longest variables.


## Example Output
```sh
$ robot-cli testcases
TEST FAILED: Test Case 5 - Fast
═══════════════════════════════
▶ BuiltIn.Log('Starting Test Case 5')
  I Starting Test Case 5
  ✓ PASS     0s
▶ BuiltIn.Create List('1', '2')
  I ${list} = ['1', '2']
  ✓ PASS     0s
▶ Collections.Append To List('${list}', '4')
  ✓ PASS     0s
▶ BuiltIn.Length Should Be('${list}', '4')
  I Length is 3.
  F Length of '['1', '2', '4']' should be 4 but is 3.
  ✗ FAIL     0s
▶ BuiltIn.Log('Test Case 5 completed.')
  → SKIP     0s

┌──────────────────────────────────────────────────────────────────────┐
│ [SUITE] Suite 2                                                      │
│ [TEST 11/16] Test Case 3 - Slow    (elapsed  4s, ETA  3s)            │
│ [BuiltIn.Sleep]  '${DELAY_LONG}                                      │
└──────────────────────────────────────────────────────────────────────┘
```

## Requirements
- Python 3.6+
- Robot Framework 4.0+

## Contributing
Contributions, bugs, and feature requests are welcome! Please submit a pull
request or open an issue for bugs and requests.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file
for details.
