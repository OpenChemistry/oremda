#!/usr/bin/env python
import json
import os

from oremda.clients import Client as ContainerClient
from oremda.plasma_client import PlasmaClient
from oremda.registry import Registry
from oremda.constants import (
    DEFAULT_PLASMA_SOCKET_PATH,
    DEFAULT_DATA_DIR,
    DEFAULT_OREMDA_VAR_DIR,
)
from oremda.utils.plasma import start_plasma_store
from oremda.typing import ContainerType
import oremda.pipeline

if "SINGULARITY_BIND" in os.environ:
    # This means we are running singularity
    container_type = ContainerType.Singularity

    # Remove this so we don't repeat the parent container's bind mounting
    del os.environ["SINGULARITY_BIND"]
else:
    container_type = ContainerType.Docker

plasma_kwargs = {
    "memory": 50_000_000,
    "socket_path": DEFAULT_PLASMA_SOCKET_PATH,
}

with start_plasma_store(**plasma_kwargs):
    plasma_client = PlasmaClient(DEFAULT_PLASMA_SOCKET_PATH)
    container_client = ContainerClient(container_type)

    registry = Registry(plasma_client, container_client)

    run_kwargs = {
        "volumes": {
            DEFAULT_OREMDA_VAR_DIR: {"bind": DEFAULT_OREMDA_VAR_DIR},
            DEFAULT_DATA_DIR: {"bind": DEFAULT_DATA_DIR},
            "/oremda": {"bind": "/oremda"},
        },
        "detach": True,
        "working_dir": DEFAULT_DATA_DIR,
    }

    if container_type == ContainerType.Docker:
        # Get the child containers to share IPC with the parent
        self_container = container_client.self_container()
        run_kwargs["ipc_mode"] = f"container:{self_container.id}"

    registry.run_kwargs = run_kwargs

    with open("/runner/pipeline.json") as f:
        pipeline_obj = json.load(f)

    pipeline = oremda.pipeline.deserialize_pipeline(
        pipeline_obj, plasma_client, registry
    )
    pipeline.run()
    registry.release()
