import typer  # type: ignore[import]

app = typer.Typer()


@app.callback()
def callback():
    """
    Test help message short desc

    Test help message long desc
    """
    pass


@app.command()
def hello(name: str = typer.Argument(..., help="Test argument")):
    """
    Test help message short desc

    Test help message long desc
    """
    typer.echo(f"Hello {name}")
    pass
