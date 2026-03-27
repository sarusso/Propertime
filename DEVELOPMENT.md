# Development

This project uses [uv](https://docs.astral.sh/uv/) for dependency management and [hatchling](https://hatch.pypa.io/) as the build backend.


## Setup

Install uv if you don't have it yet (see [uv installation docs](https://docs.astral.sh/uv/getting-started/installation/)), then:

    uv sync

This creates a virtual environment and installs all dependencies, including dev tools like Jupyter.


## Running the Jupyter notebook

    uv run jupyter notebook Quickstart.ipynb


## Testing

### Run all tests

    ./propertime/tests/run_all.sh

This runs dependency sync, unit tests, and the e2e notebook test in sequence.

### Unit tests

    uv run python -m unittest discover

### End-to-end notebook test

Executes the Quickstart notebook and fails if any cell raises an error:

    ./propertime/tests/e2e/test_notebook.sh

### Multi-version regression tests

Uses Docker to test against Python 3.6 through 3.13:

    ./regression_test.sh


## CI

GitHub Actions runs both unit tests and the e2e notebook test on every push and pull request to `main`. The workflow is defined in `.github/workflows/ci.yml`.


## Versioning

This project follows [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html). The version is defined in `pyproject.toml` under `[project].version`.


## Publishing to PyPI

The `pypi.sh` script handles building and publishing:

    ./pypi.sh build      # Build sdist and wheel
    ./pypi.sh testpush   # Upload to Test PyPI
    ./pypi.sh push       # Upload to PyPI
    ./pypi.sh clean      # Remove build artifacts
