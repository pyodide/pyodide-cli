from collections import defaultdict
from gettext import gettext
from typing import override
import sys
from functools import cache
from importlib.metadata import Distribution, EntryPoint
from importlib.metadata import distribution as importlib_distribution
from importlib.metadata import entry_points

import click  # type: ignore[import]
import typer  # type: ignore[import]
from typer.main import TyperInfo, solve_typer_info_help  # type: ignore[import]

from . import __version__


class OriginGroup(click.Group):
    """A click Group to support grouped command help message by its origin."""

    origin_map: defaultdict[str, str] = defaultdict()

    @override
    def add_command(
        self, cmd: click.Command, name: str | None = None, *, origin: str | None = None
    ) -> None:
        """
        Register click commands with its origin.
        """
        # if name is not provided, command name is used
        if name is None:
            name = cmd.name
        if name is None:
            name = ""  # FIXME: not the bes gt way?
        if origin is None:
            origin = ""

        self.origin_map[name] = origin
        super().add_command(cmd, name)

    @override
    def format_commands(self, ctx: click.Context, formatter: click.HelpFormatter):
        """
        Format commands grouped by origin, similar to rich formatting.
        The rest of the behavior is similar to click.Group.format_commands.
        """
        names = self.list_commands(ctx)

        # list of (origin, name, cmd)
        commands: list[tuple[str, str, click.Command]] = []

        for name in names:
            cmd = self.get_command(ctx, name)
            if cmd is None:
                continue
            if cmd.hidden:
                continue

            commands.append((name, self.origin_map.get(name, ""), cmd))

        # sort by its origin, then by command name
        commands.sort(key=lambda elem: (elem[1], elem[0]))

        if len(commands):
            limit = formatter.width - 6 - max(len(cmd[0]) for cmd in commands)

            last_source: str = ""
            rows = []

            def write_row():
                if rows:
                    if len(last_source):
                        source_desc = f" Registered by: {last_source}"
                    else:
                        source_desc = ""
                    # NOTE: gettext is used in click! Any i18n support?
                    with formatter.section(f"{gettext('Commands')}{source_desc}"):
                        formatter.write_dl(rows)
                rows.clear()

            for name, source, cmd in commands:
                if last_source != source:
                    write_row()

                help = cmd.get_short_help_str(limit)
                rows.append((name, help))
                last_source = source

            write_row()


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


@click.group(cls=OriginGroup, invoke_without_command=True)
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
            cli.add_command(module, name=plugin_name, origin=pkgname)
        elif callable(module):
            typer_kwargs = getattr(module, "typer_kwargs", None)
            # construct Typer app and preserve typer_kwargs as of now
            if typer_kwargs is not None:
                app = typer.Typer()
                app.command(
                    plugin_name,
                    help=help_with_origin,
                    **typer_kwargs,
                )(module)
                cmd = typer.main.get_command(app)
            else:
                # we need a new command with an updated help message
                # set module (whether it is click, typer, or any other callable) as callback
                cmd = click.Command(
                    plugin_name,
                    callback=module,
                    help=help_with_origin,
                )

            cli.add_command(
                cmd,
                origin=pkgname,
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
