import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from oremda.typing import IdType

from server.context import GlobalContext
from server.api.api_v1.api import api_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


async def run_pipeline(session_id: IdType, pipeline_id: IdType, context: GlobalContext):
    pipeline_ids = context.session_pipelines.get(session_id, set())
    if pipeline_id not in pipeline_ids:
        return

    model = context.pipelines[pipeline_id]
    pipeline = model.pipeline

    # pipeline.run is a blocking function, run it in a separate thread to free the
    # server to perform other tasks such as sending notifications
    # TODO: convert pipeline.run to an async function
    await asyncio.to_thread(pipeline.run)
