# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.2] - unreleased
### Changed
 - `pyodide --help` will now group subcommands by their package name.
   ([#19](https://github.com/pyodide/pyodide-cli/pull/19))

## [0.2.1] - 2022-12-20
### Added
 - Define `pyodide_cli.app.typer_click_object` when `pyodide_cli` is imported from within sphinx,
   to allow auto-generate CLI documentation with [sphinx-click](https://sphinx-click.readthedocs.io/en/latest/)
   ([#17](https://github.com/pyodide/pyodide-cli/pull/17))


## [0.2.0] - 2022-09-04
### Added
 - When registering commands, you can pass extra arguments to the typer's `app.command` method, by setting
   CLI entry point function attribute `typer_kwargs` to the corresponding kwargs dict.
   ([#2](https://github.com/pyodide/pyodide-cli/pull/2))

### Changed

 - Fix entry point registration for callable functions ([#4](https://github.com/pyodide/pyodide-cli/pull/4))

## [0.1.0] - 2022-09-02

Initial release
