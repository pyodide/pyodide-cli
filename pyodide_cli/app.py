import sys
from functools import cache
from importlib.metadata import Distribution, EntryPoint
from importlib.metadata import distribution as importlib_distribution
from importlib.metadata import entry_points

import click
import typer  # type: ignore[import]
from typer.main import TyperInfo, solve_typer_info_help  # type: ignore[import]

from . import __version__


def version_callback(
    ctx: click.Context, _param: click.Option, value: bool | None
) -> None:
    if not value or ctx.resilient_parsing:
        return

    click.echo(f"pyodide CLI version: {__version__}")

    eps = entry_points(group="pyodide.cli")
    # filter out duplicate pkgs
    pkgs = {_entrypoint_to_pkgname(ep): _entrypoint_to_version(ep) for ep in eps}
    for pkg, version in pkgs.items():
        click.echo(f"{pkg} version: {version}")

    ctx.exit()


@click.group(invoke_without_command=True)
@click.option(
    "--version",
    is_flag=True,
    is_eager=True,
    callback=version_callback,
    expose_value=False,
    help="Show the version of the Pyodide CLI",
)
@click.pass_context
def cli(ctx: click.Context):
    """A command line interface for Pyodide.

    Other CLI subcommands are registered via the plugin system by installing
    Pyodide ecosystem packages (e.g. pyodide-build, pyodide-pack,
    auditwheel-emscripten, etc.)
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


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
        else:
            help_with_origin = _inject_origin(
                getattr(module, "__doc__", ""), origin_text
            )

        if isinstance(module, click.Group):
            cli.add_command(module, name=plugin_name)
        elif callable(module):
            cli.add_command(
                click.Command(plugin_name, callback=module, help=help_with_origin)
            )
        else:
            raise RuntimeError(f"Invalid plugin: {plugin_name}")


def main():
    register_plugins()
    cli()


if "sphinx" in sys.modules and __name__ != "__main__":
    # Create the typer click object to generate docs with sphinx-click
    register_plugins()
    typer_click_object = cli

if __name__ == "__main__":
    main()
