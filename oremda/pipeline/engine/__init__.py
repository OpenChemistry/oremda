import asyncio
import logging
import sys
import coloredlogs
import signal

from oremda.typing import ContainerType
from oremda.clients.singularity import SingularityClient
from oremda.pipeline.engine.rpc.client import RpcClient
from oremda.pipeline.engine.context import pipeline_context
from oremda.pipeline.engine.config import settings

# Setup logger
logger = logging.getLogger("engine")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = coloredlogs.ColoredFormatter(
    "%(asctime)s,%(msecs)03d - %(name)s - %(levelname)s - %(message)s"
)
handler.setFormatter(formatter)
logger.addHandler(handler)


async def run():
    # Set the Singularity image path if we are using Singularity
    if settings.OREMDA_CONTAINER_TYPE == ContainerType.Singularity:
        SingularityClient.images_dir = settings.OREMDA_SINGULARITY_IMAGE_DIR

    with pipeline_context() as context:
        async with RpcClient(settings.SERVER_URL, context) as client:
            logger.info("Connected to server.")
            await client.wait_on_reader()


async def shutdown(signal, loop, run_task):

    logger.info(f"Received exit signal {signal.name}...")
    logger.info("Canceling engine task.")

    if run_task is not None:
        run_task.cancel()

    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]

    if len(tasks) > 0:
        logger.info(f"Waiting for {len(tasks)} to complete.")
        await asyncio.wait(tasks)
    logger.info("Stopping event loop.")
    loop = asyncio.get_event_loop()
    loop.stop()


def start():
    logger.info("Starting pipeline engine.")
    loop = asyncio.get_event_loop()
    run_task = loop.create_task(run())

    signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
    for s in signals:
        loop.add_signal_handler(
            s, lambda s=s: asyncio.create_task(shutdown(s, loop, run_task))
        )

    loop.run_forever()
