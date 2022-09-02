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


def register_plugins():
    eps = entry_points(group="pyodide.cli")
    plugins = {ep.name: ep.load() for ep in eps}
    for plugin_name, module in plugins.items():
        if isinstance(module, typer.Typer):
            app.add_typer(module, name=plugin_name)
        elif callable(module):
            context_settings = getattr(module, "typer_context_settings", {})
            kwargs = {}
            if context_settings:
                kwargs = {"context_settings": context_settings}
            app.command(plugin_name, **kwargs)(module)
        else:
            raise RuntimeError(f"Invalid plugin: {plugin_name}")


def main():
    register_plugins()
    app()


if __name__ == "__main__":
    main()
