import click
import uvicorn


@click.command(
    "server",
    short_help="oremda server",
    help="Run the oremda server.",
)
def main():
    uvicorn.run("oremda.server.main:app")
