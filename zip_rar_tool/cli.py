import typer

from zip_rar_tool import core

app = typer.Typer()


@app.command()
def extract(
    archive: str = typer.Argument(..., help="Path to archive file"),
    output: str = typer.Argument(".", help="Output directory"),
    password: str = typer.Option(None, "--password", "-p", help="Archive password"),
):
    core.extract(archive, output, password)
    typer.echo(f"Extracted to {output}")


@app.command()
def list(
    archive: str = typer.Argument(..., help="Path to archive file"),
):
    files = core.list_files(archive)
    for f in files:
        typer.echo(f"{f['filename']:50s} {f['size']:>10d}")


@app.command()
def compress(
    source: str = typer.Argument(..., help="Source directory"),
    output: str = typer.Argument(..., help="Output archive path"),
    password: str = typer.Option(None, "--password", "-p", help="Archive password"),
):
    core.compress(source, output, password)
    typer.echo(f"Created {output}")
