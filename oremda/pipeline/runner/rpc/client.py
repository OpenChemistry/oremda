import asyncio
from typing import Dict
from fastapi_websocket_rpc import RpcMethodsBase, WebSocketRpcClient

from oremda.typing import DisplayType, IdType, JSONType, PipelineJSON
from oremda.pipeline.runner.context import GlobalContext, SessionWebModel, SessionModel
from oremda.pipeline.messages import NotificationMessage, pipeline_created
from oremda.pipeline.observer import ServerPipelineObserver
from oremda.pipeline.displays import DisplayHandle1D, DisplayHandle2D
from oremda.pipeline.models import PipelineModel, SerializablePipelineModel
from oremda.pipeline import deserialize_pipeline
from oremda.display import NoopDisplayHandle
from oremda.utils.id import unique_id
from oremda.pipeline.runner.config import settings
from oremda.clients import Client


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
    while True:
        msg = await queue.get()
        await client.notify_clients(msg.dict(), session_id)


class PipelineRunnerMethods(RpcMethodsBase):
    def __init__(self, context: GlobalContext, client: RpcClient):
        self.context = context
        self.client = client

    async def run(self, session_id: IdType, pipeline_definition: PipelineJSON) -> Dict:
        pipeline_definition = PipelineJSON(**pipeline_definition)

        pipeline_id = unique_id()
        pipeline_definition.id = pipeline_id

        queue = asyncio.Queue()
        asyncio.create_task(notify_clients(session_id, queue, self.client))

        def notify(message: NotificationMessage):
            queue.put_nowait(message)

        def display_factory(id: IdType, display_type: DisplayType):
            if display_type == DisplayType.OneD:
                return DisplayHandle1D(id, notify)
            elif display_type == DisplayType.TwoD:
                return DisplayHandle2D(id, notify)
            else:
                return NoopDisplayHandle(id, display_type)

        pipeline = deserialize_pipeline(
            pipeline_definition.dict(by_alias=True),
            self.context.plasma_client,
            self.context.registry,
            display_factory,
        )

        pipeline.observer = ServerPipelineObserver(notify)

        model = PipelineModel(
            id=pipeline_id, graph=pipeline_definition, pipeline=pipeline
        )

        web_session = self.context.sessions.setdefault(
            session_id, SessionWebModel(session=SessionModel(id=session_id))
        )

        pipeline_ids = web_session.pipelines
        pipeline_ids.add(model.id)

        self.context.pipelines[model.id] = model

        message = pipeline_created(model)

        asyncio.create_task(self.client.notify_clients(message.dict(), session_id))

        asyncio.create_task(run_pipeline(session_id, model.id, self.context))

        return SerializablePipelineModel(
            id=pipeline_id, graph=pipeline_definition
        ).dict(by_alias=True)

    async def get_available_operators(self, session_id: IdType) -> Dict:
        operators = {}

        for image in Client(settings.OREMDA_CONTAINER_TYPE).images():
            operators[image.name] = image.labels

        return operators
