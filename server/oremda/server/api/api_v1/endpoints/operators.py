from fastapi import Query, HTTPException, APIRouter

from oremda.typing import IdType
import oremda.server as server

router = APIRouter()


@router.get("")
async def get_available_operators(session_id: IdType = Query(..., alias="sessionId")):
    # if session_id not in context.sessions:
    #     raise Exception(f"Session {session_id} does not exist")

    if server.pipeline_runner is None:  # type: ignore
        raise HTTPException(status_code=503, detail="Pipeline engine not connected!")

    runner = server.pipeline_runner  # type: ignore
    response = await runner.other.get_available_operators(session_id=session_id)

    return response.result
