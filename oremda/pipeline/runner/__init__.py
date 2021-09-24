import asyncio
from oremda.typing import ContainerType
from oremda.clients.singularity import SingularityClient
from oremda.pipeline.runner.rpc.client import RpcClient
from oremda.pipeline.runner.context import pipeline_context
from oremda.pipeline.runner.config import settings


async def run():
    # Set the Singularity image path if we are using Singularity
    if settings.OREMDA_CONTAINER_TYPE == ContainerType.Singularity:
        SingularityClient.images_dir = settings.OREMDA_SINGULARITY_IMAGE_DIR

    with pipeline_context() as context:
        async with RpcClient(settings.SERVER_URL, context) as client:
            await client.wait_on_reader()


def start():
    asyncio.get_event_loop().run_until_complete(run())
