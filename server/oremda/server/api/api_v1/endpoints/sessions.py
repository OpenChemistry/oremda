from typing import List
from fastapi import APIRouter


from oremda.models import SessionModel

from oremda.server.context import context
from oremda.server.utils import unique_id

router = APIRouter()


@router.get("", response_model=List[SessionModel])
async def get_sessions():
    return list(context.sessions.values())


@router.post("", response_model=SessionModel)
async def create_session():
    session_id = unique_id()
    session = SessionModel(id=session_id)
    context.sessions[session_id] = session

    return session
