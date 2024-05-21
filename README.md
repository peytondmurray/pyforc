[![MIT license](https://img.shields.io/badge/License-MIT-blue.svg)](https://lbesson.mit-license.org/)

# pyforc

FORC analysis in Python.
![A FORC distribution plot.](./assets/forc.jpg)

## Installation

### Install from PyPI

The easiest way to get started is by installing via `pip`:

`pip install pyforc`

This will grab the latest published release on the Python Package Index and
install it to your current python environment.

### Installation from source

Install from source by doing

`pip install git+https://github.com/peytondmurray/pyforc`

Alternatively you can clone this repo and run

`pip install .`

## Contributions

Contributions are welcome - open an issue or create a pull request. I'm trying
to stick to PEP8 as much as I can, except I'm using line lengths of 100
characters. I'm using numpydoc formatting for the documentation as well. Don't
worry too much about this stuff though, we can work together to integrate your
code.

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
