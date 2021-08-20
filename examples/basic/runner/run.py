#!/usr/bin/env python
import json

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

plasma_kwargs = {
    "memory": 50_000_000,
    "socket_path": DEFAULT_PLASMA_SOCKET_PATH,
}

with start_plasma_store(**plasma_kwargs):
    plasma_client = PlasmaClient(DEFAULT_PLASMA_SOCKET_PATH)
    container_client = ContainerClient(ContainerType.Docker)

    registry = Registry(plasma_client, container_client)

    self_container = container_client.self_container()

    run_kwargs = {
        "volumes": {
            mount.source: {"bind": mount.destination} for mount in self_container.mounts
        },
        "ipc_mode": f"container:{self_container.id}",
        "detach": True,
        "working_dir": DEFAULT_DATA_DIR,
    }

    # Add the oremda var dir mount
    run_kwargs["volumes"][DEFAULT_OREMDA_VAR_DIR] = {"bind": DEFAULT_OREMDA_VAR_DIR}

    registry.run_kwargs = run_kwargs

    with open("/runner/pipeline.json") as f:
        pipeline_obj = json.load(f)

    pipeline = oremda.pipeline.deserialize_pipeline(
        pipeline_obj, plasma_client, registry
    )
    pipeline.run()

    registry.release()
