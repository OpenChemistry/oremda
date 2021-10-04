import asyncio
from typing import Dict
from fastapi_websocket_rpc import RpcMethodsBase, WebSocketRpcClient

from oremda.typing import DisplayType, IdType, JSONType, PipelineJSON
from oremda.pipeline.engine.context import GlobalContext, SessionWebModel, SessionModel
from oremda.pipeline.engine.rpc.messages import NotificationMessage, pipeline_created
from oremda.pipeline.engine.rpc.observer import ServerPipelineObserver
from oremda.pipeline.engine.rpc.models import PipelineModel, SerializablePipelineModel
from oremda.pipeline import deserialize_pipeline
from oremda.display import NoopDisplayHandle
from oremda.utils.id import unique_id
from oremda.pipeline.engine.config import settings
from oremda.clients import Client
from oremda.pipeline.engine.rpc.displays import (
    RemoteRenderDisplayHandle1D,
    RemoteRenderDisplayHandle2D,
)


class RpcClient(WebSocketRpcClient):
    def __init__(self, uri: str, context: GlobalContext):
        super().__init__(
            uri, methods=PipelineRunnerMethods(context, self)  # type: ignore
        )

    async def notify_clients(self, message: JSONType, session_id: IdType):
        await self.other.notify_clients(message=message, session_id=session_id)


async def run_pipeline(session_id: IdType, pipeline_id: IdType, context: GlobalContext):
    pipeline_ids = set({})
    web_session = context.sessions.get(session_id)
    if web_session is not None:
        pipeline_ids = web_session.pipelines

    if pipeline_id not in pipeline_ids:
        return

    model = context.pipelines[pipeline_id]
    pipeline = model.pipeline

    # pipeline.run is a blocking function, run it in a separate thread to free the
    # server to perform other tasks such as sending notifications
    # TODO: convert pipeline.run to an async function
    await asyncio.to_thread(pipeline.run)


async def notify_clients(session_id, queue: asyncio.Queue, client: RpcClient):
    async def process_message():
        msg = await queue.get()
        await client.notify_clients(msg.dict(), session_id)

    try:
        while True:
            await process_message()
    except asyncio.CancelledError:
        while not queue.empty():
            await process_message()


class PipelineRunnerMethods(RpcMethodsBase):
    def __init__(self, context: GlobalContext, client: RpcClient):
        self.context = context
        self.client = client

    async def run(self, session_id: IdType, pipeline_definition: dict) -> Dict:
        pipeline_json = PipelineJSON(**pipeline_definition)

        pipeline_id = unique_id()
        pipeline_json.id = pipeline_id

        queue = asyncio.Queue()
        notify_task = asyncio.create_task(
            notify_clients(session_id, queue, self.client)
        )

        def cleanup_notify_task(context) -> None:
            notify_task.cancel()

        def notify(message: NotificationMessage):
            queue.put_nowait(message)

        def display_factory(id: IdType, display_type: DisplayType):
            if display_type == DisplayType.OneD:
                return RemoteRenderDisplayHandle1D(id, notify)
            elif display_type == DisplayType.TwoD:
                return RemoteRenderDisplayHandle2D(id, notify)
            else:
                return NoopDisplayHandle(id, display_type)

        pipeline = deserialize_pipeline(
            pipeline_json.dict(by_alias=True),
            self.context.plasma_client,
            self.context.registry,
            display_factory,
        )

        pipeline.observer = ServerPipelineObserver(notify)

        model = PipelineModel(id=pipeline_id, graph=pipeline_json, pipeline=pipeline)

        web_session = self.context.sessions.setdefault(
            session_id, SessionWebModel(session=SessionModel(id=session_id))
        )

        pipeline_ids = web_session.pipelines
        pipeline_ids.add(model.id)

        self.context.pipelines[model.id] = model

        message = pipeline_created(model)

        asyncio.create_task(self.client.notify_clients(message.dict(), session_id))

        pipeline_task = asyncio.create_task(
            run_pipeline(session_id, model.id, self.context)
        )
        pipeline_task.add_done_callback(cleanup_notify_task)

        return SerializablePipelineModel(id=pipeline_id, graph=pipeline_json).dict(
            by_alias=True
        )

    async def get_available_operators(self, session_id: IdType) -> Dict:
        operators = {}

        for image in Client(settings.OREMDA_CONTAINER_TYPE).images():
            operators[image.name] = image.labels

        return operators
