
## Setup

Use a virtualenv, and install the library with its `dev` dependencies.

```bash
python -m virtualenv .venv
. .venv/bin/activate

git clone git@github.com:nerdocs/conjunto.git
python -m pip install .[dev]
```

## Code conventions

* Format everything using [black](https://black.readthedocs.io).
* Write documentation for your code.

## Coding

#### Version upgrade

In `conjunto/__init__.py`, upgrade `__version__`, using [Semantic versioning](https://semver.org).
```python
__version__ = "1.2.3"
```

## Package management

#### Build package

```bash
$ make build
```

#### Deploy package

```bash
make publish
```
