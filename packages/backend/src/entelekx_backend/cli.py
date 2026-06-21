"""CLI entrypoint."""

import typer
import uvicorn

from entelekx_backend.core.config import get_settings

cli = typer.Typer(help="EntelekX backend CLI")


@cli.command()
def serve(
    host: str = "127.0.0.1",
    port: int = 7349,
    reload: bool = False,
):
    """Run the EntelekX backend server."""
    settings = get_settings()
    uvicorn.run(
        "entelekx_backend.main:app",
        host=host or settings.host,
        port=port or settings.port,
        reload=reload,
    )


@cli.command()
def version():
    """Print the backend version."""
    typer.echo(get_settings().version)


def main():
    cli()


if __name__ == "__main__":
    main()
