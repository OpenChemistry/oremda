#!/usr/bin/env python
import click
from oremda.pipeline.runner import start


@click.command(
    "runner",
    short_help="oremda runner",
    help="Run the pipeline runner service.",
)
def main():
    start()
