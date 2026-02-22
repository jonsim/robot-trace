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

### 5. Running locally
After installing in editable mode, you can test your changes by running the
command line tool against the sample test cases provided in the
`tests/minimal_testcases` directory:
```sh
robot-trace tests/minimal_testcases
```

Alternatively, try running it directly as a module:
```sh
robot --listener robot_trace --console=none tests/minimal_testcases
```

### 6. Running tests
To run the unit tests:
```sh
python -m unittest discover tests/unit
```

To run the unit tests and view the coverage report:
```sh
coverage run -m unittest discover tests/unit
coverage report -m
```

To run the system tests:
```sh
robot tests/system
```


## Submitting Changes
1. Make your changes in a new branch.
2. Ensure you have run the unit and system tests locally.
3. Ensure that all `pre-commit` hooks pass successfully.
4. Open a Pull Request!
