#!/usr/bin/env python
import click
from oremda.pipeline.runner import start


@click.command(
    "engine",
    short_help="oremda engine",
    help="Run the pipeline engine.",
)
def main():
    start()
