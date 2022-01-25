from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from oremda.server.api.api_v1.api import api_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

# If we have the oremda-client package install
try:
    from oremda.client import client_build  # type: ignore

    print(client_build)
    app.mount("/", client_build, name="client")
except ImportError:
    import traceback

    traceback.print_exc()
    print("iomport")
    pass
