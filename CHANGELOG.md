# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2022-09-02
### Added
 - When registering commands, you can pass extra arguments to the typer's `app.command` method, by setting
   CLI entry point function attribute `typer_kwargs` to the corresponding kwargs dict.
   ([#4](https://github.com/pyodide/pyodide-cli/pull/2))

### Changed

 - Fix entry point registration for callable functions ([#4](https://github.com/pyodide/pyodide-cli/pull/2))

## [0.1.0] - 2022-09-02

Initial release
