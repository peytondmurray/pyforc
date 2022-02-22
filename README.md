[![codecov](https://codecov.io/gh/peytondmurray/PyFORC/branch/develop/graph/badge.svg?token=0fxoMUIK6x)](https://codecov.io/gh/peytondmurray/PyFORC)
[![MIT license](https://img.shields.io/badge/License-MIT-blue.svg)](https://lbesson.mit-license.org/)

# PyFORC

FORC analysis in Python.
![forc]

## Installation

Install by cloning this repo and running

`pip install .`

## Contributions

Contributions are welcome - open an issue or create a pull request. I'm trying
to stick to PEP8 as much as I can, except I'm using line lengths of 100
characters. I'm using numpydoc formatting for the documentation as well. Don't
worry too much about this stuff though, we can work together to integrate your
code.

[forc]: https://github.com/peytondmurray/PyFORC/blob/develop/assets/forc.jpg

### Pre-commit hooks

This project makes use of [pre-commit hooks](https://pre-commit.com/) for
linting and style checking. If you haven't used pre-commit hooks before, first
install pre commit:

```bash
pip install pre-commit
```

Then inside the repository install the hooks themselves:

```bash
pre-commit install
```

Now, pre-commit hooks will run automatically any time you type `git commit`.
