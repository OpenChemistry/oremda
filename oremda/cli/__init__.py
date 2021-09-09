from click_plugins import with_plugins
from pkg_resources import iter_entry_points
import click

@with_plugins(iter_entry_points('oremda.cli.plugins'))
@click.group(help='oremda: open reproducible electron microscopy data analysis.',
             context_settings=dict(help_option_names=['-h', '--help']))
def main():
    pass