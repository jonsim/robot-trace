# Contributing

## Local Development

To build and run the project locally, follow these steps:

### 1. Prerequisites
- Python 3.6+
- pip 26.0+

### 2. Setup a virtual environment
It is recommended to use a virtual environment for development to avoid
conflicting with system-wide packages:
```sh
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
```

### 3. Install dependencies
Install the project in editable mode along with the development dependencies:
```sh
pip install -e '.[dev]'
```

### 4. Install pre-commit hooks
This project uses `pre-commit` to ensure code formatting and linting standards
are consistently met. `ruff` is used for both fixing and formatting python code.

Install the git hooks to run automatically before every commit:
```sh
pre-commit install
```

### 5. Running the CLI Locally
After installing in editable mode, you can test your changes by running the CLI
against the sample test cases provided in the `testcases/` folder:
```sh
robot-cli testcases
```

Alternatively, try running it directly as a module:
```sh
robot --listener CLIProgress --console=none testcases
```

## Submitting Changes
1. Make your changes in a new branch.
2. Ensure you have run tests locally (e.g. against the provided `testcases` or
   any new test suites you created).
3. Ensure that all `pre-commit` hooks pass successfully.
4. Open a Pull Request!
