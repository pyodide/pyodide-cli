import click  # type: ignore[import]


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx: click.Context) -> None:
    """
    Test help message short desc

    Test help message long desc
    """
    pass
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cli.command()
@click.argument("name", required=True)
def hello(name: str) -> None:
    """
    Test help message short desc

    Test help message long desc
    """
    click.echo(f"Hello {name}")
