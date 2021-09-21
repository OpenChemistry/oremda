from fastapi import APIRouter

from server.api.api_v1.endpoints import sessions, pipelines, websockets, rpc

api_router = APIRouter()

api_router.include_router(sessions.router, prefix="/sessions", tags=["files"])
api_router.include_router(pipelines.router, prefix="/pipelines", tags=["pipelines"])
api_router.include_router(websockets.router, prefix="/ws", tags=["ws"])
api_router.include_router(rpc.router, prefix="/rpc", tags=["rpc"])
