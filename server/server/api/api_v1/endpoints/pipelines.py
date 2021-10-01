from typing import List
from fastapi import Query, Body, HTTPException, APIRouter


from oremda.typing import IdType, PipelineJSON

from oremda.pipeline.engine.rpc.models import (
    SerializablePipelineModel,
)

from server.context import context
import server

router = APIRouter()


@router.get("", response_model=List[SerializablePipelineModel])
async def get_pipelines(session_id: IdType = Query(..., alias="sessionId")):
    if session_id not in context.sessions:
        raise Exception(f"Session {session_id} does not exist")

    pipeline_ids = context.session_pipelines.get(session_id, set())

    pipelines = list(
        map(lambda pipeline_id: context.pipelines[pipeline_id], pipeline_ids)
    )

    return pipelines


@router.post("", response_model=SerializablePipelineModel)
async def create_pipeline(
    session_id: IdType = Query(..., alias="sessionId"),
    graph: PipelineJSON = Body(...),
):

    if server.pipeline_runner is None:  # type: ignore
        raise HTTPException(status_code=503, detail="Pipeline runner not connected!")

    response = await server.pipeline_runner.other.run(  # type: ignore
        session_id=session_id, pipeline_definition=graph.dict(by_alias=True)
    )

    return response.result
