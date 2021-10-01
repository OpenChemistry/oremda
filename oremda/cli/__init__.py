from click_plugins import with_plugins
from pkg_resources import iter_entry_points
import click
import logging
import sys
import coloredlogs

# Setup logger
logger = logging.getLogger("oremda")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = coloredlogs.ColoredFormatter(
    "%(asctime)s,%(msecs)03d - %(name)s - %(levelname)s - %(message)s"
)
handler.setFormatter(formatter)
logger.addHandler(handler)


@with_plugins(iter_entry_points("oremda.cli.plugins"))
@click.group(
    help="oremda: open reproducible electron microscopy data analysis.",
    context_settings=dict(help_option_names=["-h", "--help"]),
)
def main():
    pass
