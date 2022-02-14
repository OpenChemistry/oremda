import asyncio
import click
import logging
import coloredlogs
import sys
import signal

# Setup logger
logger = logging.getLogger("start")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = coloredlogs.ColoredFormatter(
    "%(asctime)s,%(msecs)03d - %(name)s - %(levelname)s - %(message)s"
)
handler.setFormatter(formatter)
logger.addHandler(handler)


async def shutdown(signal, loop, tasks):

    logger.info(f"Received exit signal {signal.name}...")
    logger.info("Canceling engine task.")

    for task in tasks:
        task.cancel()

    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]

    if len(tasks) > 0:
        logger.info(f"Waiting for {len(tasks)} to complete.")
        await asyncio.wait(tasks)
    logger.info("Stopping event loop.")
    loop = asyncio.get_event_loop()
    loop.stop()


async def start_server():
    proc = await asyncio.create_subprocess_shell("uvicorn oremda.server.main:app")

    await proc.communicate()


async def start_engine():
    proc = await asyncio.create_subprocess_shell("oremda engine")

    await proc.communicate()


@click.command(
    "start",
    short_help="oremda start",
    help="Run the oremda stack.",
)
def main():
    loop = asyncio.get_event_loop()
    server_task = loop.create_task(start_server())
    engine_task = loop.create_task(start_engine())

    signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
    for s in signals:
        loop.add_signal_handler(
            s,
            lambda s=s: asyncio.create_task(
                shutdown(s, loop, [server_task, engine_task])
            ),
        )

    loop.run_forever()
