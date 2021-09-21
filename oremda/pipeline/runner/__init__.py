import asyncio
from oremda.pipeline.runner.rpc.client import RpcClient
from oremda.pipeline.runner.context import pipeline_context
from oremda.pipeline.runner.config import settings


async def run():
    with pipeline_context() as context:
        async with RpcClient(settings.SERVER_URL, context) as client:
            await client.wait_on_reader()


def start():
    asyncio.get_event_loop().run_until_complete(run())
