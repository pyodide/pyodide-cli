# pyodide-cli

[![PyPI Latest Release](https://img.shields.io/pypi/v/pyodide-cli.svg)](https://pypi.org/project/pyodide-cli/)
![GHA-main](https://github.com/pyodide/pyodide-cli/actions/workflows/main.yml/badge.svg)
![GHA-release](https://github.com/pyodide/pyodide-cli/actions/workflows/release.yml/badge.svg)
[![codecov](https://codecov.io/gh/pyodide/pyodide-cli/branch/main/graph/badge.svg)](https://codecov.io/gh/pyodide/pyodide-cli)

The command line interface for the Pyodide project.

In most cases, you do not need to install this package directly, and it would be installed as
a dependency of other packages in the ecosystem (e.g., pyodide-build, pyodide-pack, auditwheel-emscripten, etc.)

## Installation

```
pip install pyodide-cli
```

## Usage

To get a list of available CLI commands,
```
pyodide --help
```

## Developers

You can register a subcommand in the `pyodide` CLI in your own package by:

1. adding a dependency on `pyodide-cli`
2. Adding a `pyodide.cli` [entry point](https://setuptools.pypa.io/en/latest/userguide/entry_point.html). For example, with

   **setup.cfg**
   ```toml
   [options.entry_points]
   pyodide.cli =
    do_something = "<your-package>.cli:main"
   ```

   or

   **pyproject.toml**
   ```toml
   [project.entry-points."pyodide.cli"]
   do_something = "<your-package>.cli:main"
   ```

   where in this example `main` needs to be a function with type annotations
   that can be converted to a CLI with [typer](https://typer.tiangolo.com/).


## License

pyodide-cli uses the [Mozilla Public License Version
2.0](https://choosealicense.com/licenses/mpl-2.0/).
