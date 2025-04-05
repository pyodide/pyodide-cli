import sys
from functools import cache
from importlib.metadata import Distribution, EntryPoint
from importlib.metadata import distribution as importlib_distribution
from importlib.metadata import entry_points

import typer  # type: ignore[import]
from typer.main import TyperInfo, solve_typer_info_help  # type: ignore[import]

from . import __version__

app = typer.Typer(
    add_completion=False,
    rich_markup_mode="markdown",
    pretty_exceptions_show_locals=False,
)


def version_callback(value: bool):
    if not value:
        return

    typer.echo(f"pyodide CLI version: {__version__}")

    eps = entry_points(group="pyodide.cli")
    # filter out duplicate pkgs
    pkgs = {_entrypoint_to_pkgname(ep): _entrypoint_to_version(ep) for ep in eps}
    for pkg, version in pkgs.items():
        typer.echo(f"{pkg} version: {version}")

    raise typer.Exit()


@app.callback(no_args_is_help=True)
def callback(
    ctx: typer.Context,
    version: bool = typer.Option(
        None,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show the version of the Pyodide CLI",
    ),
):
    """A command line interface for Pyodide.

    Other CLI subcommands are registered via the plugin system by installing
    Pyodide ecosystem packages (e.g. pyodide-build, pyodide-pack,
    auditwheel-emscripten, etc.)
    """
    pass


@cache
def _entrypoint_to_distribution(entrypoint: EntryPoint) -> Distribution:
    """Find package distribution from entrypoint"""
    top_level = entrypoint.value.split(".")[0]
    dist = importlib_distribution(top_level)
    return dist


def _entrypoint_to_pkgname(entrypoint: EntryPoint) -> str:
    """Find package name from entrypoint"""
    dist = _entrypoint_to_distribution(entrypoint)
    return dist.metadata["name"]


def _entrypoint_to_version(entrypoint: EntryPoint) -> str:
    """Find package version from entrypoint"""
    dist = _entrypoint_to_distribution(entrypoint)
    return dist.metadata["version"]


def _inject_origin(docstring: str, origin: str) -> str:
    return f"{docstring}\n\n{origin}"


def register_plugins():
    """Register subcommands via the ``pyodide.cli`` entry-point"""
    eps = entry_points(group="pyodide.cli")
    plugins = {ep.name: (ep.load(), ep) for ep in eps}
    for plugin_name, (module, ep) in plugins.items():
        pkgname = _entrypoint_to_pkgname(ep)
        origin_text = f"Registered by: {pkgname}"

        if isinstance(module, typer.Typer):
            typer_info = TyperInfo(module)
            help_with_origin = _inject_origin(
                solve_typer_info_help(typer_info), origin_text
            )
            app.add_typer(
                module,
                name=plugin_name,
                rich_help_panel=origin_text,
                help=help_with_origin,
            )
        elif callable(module):
            typer_kwargs = getattr(module, "typer_kwargs", {})
            help_with_origin = _inject_origin(module.__doc__, origin_text)
            app.command(
                plugin_name,
                rich_help_panel=origin_text,
                help=help_with_origin,
                **typer_kwargs,
            )(module)
        else:
            raise RuntimeError(f"Invalid plugin: {plugin_name}")


def main():
    register_plugins()
    app()


if "sphinx" in sys.modules and __name__ != "__main__":
    # Create the typer click object to generate docs with sphinx-click
    register_plugins()
    typer_click_object = typer.main.get_command(app)

if __name__ == "__main__":
    main()
