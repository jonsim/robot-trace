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
The listener should be passed to Robot's `--listener` argument. It's recommended
to also call with: `--console=quiet` to avoid Robot's default console markers
getting interleaved.

Thus, a reasonable command line would be:
```sh
robot --listener CLIProgress.py --console=quiet path/to/tests
```

You may also consider calling with:
- `--maxerrorlines=10000` to avoid truncating all but the longest error
  messages.

## Example Output
```sh
$ robot --listener CLIProgress.py --console=quiet testcases
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
