import sys
from importlib.metadata import EntryPoint
from importlib.metadata import distribution as importlib_distribution
from importlib.metadata import entry_points

import typer  # type: ignore[import]

from . import __version__

app = typer.Typer(add_completion=False)


def version_callback(value: bool):
    if value:
        typer.echo(f"Pyodide CLI Version: {__version__}")
        raise typer.Exit()


@app.callback(no_args_is_help=True)
def callback(
    ctx: typer.Context,
    version: bool = typer.Option(
        None, "--version", callback=version_callback, is_eager=True
    ),
):
    """A command line interface for Pyodide.

    Other CLI subcommands are registered via the plugin system by installing
    Pyodide compatible packages (e.g. pyodide-build).
    """
    pass


def entrypoint_to_pkgname(entrypoint: EntryPoint) -> str:
    """Find package name from entrypoint"""

    top_level = entrypoint.value.split(".")[0]
    dist = importlib_distribution(top_level)
    return dist.metadata["name"]


def register_plugins():
    """Register subcommands via the ``pyodide.cli`` entry-point"""
    eps = entry_points(group="pyodide.cli")
    plugins = {ep.name: (ep.load(), ep) for ep in eps}
    for plugin_name, (module, ep) in plugins.items():
        pkgname = entrypoint_to_pkgname(ep)
        if isinstance(module, typer.Typer):
            app.add_typer(
                module, name=plugin_name, rich_help_panel=f"Registered by: {pkgname}"
            )
        elif callable(module):
            typer_kwargs = getattr(module, "typer_kwargs", {})
            app.command(
                plugin_name, rich_help_panel=f"Registered by: {pkgname}", **typer_kwargs
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
