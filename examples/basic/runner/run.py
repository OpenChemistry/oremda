#!/usr/bin/env python
import json

from oremda.clients import Client as ContainerClient
from oremda.shared_resources import Client as MemoryClient
from oremda.registry import Registry
from oremda.constants import DEFAULT_PLASMA_SOCKET_PATH, DEFAULT_DATA_DIR
from oremda.utils.plasma import start_plasma_store
from oremda.typing import ContainerType
import oremda.pipeline

plasma_kwargs = {
    'memory': 50_000_000,
    'socket_path': DEFAULT_PLASMA_SOCKET_PATH,
}

with start_plasma_store(**plasma_kwargs):
    memory_client = MemoryClient(DEFAULT_PLASMA_SOCKET_PATH)
    container_client = ContainerClient(ContainerType.Docker)

    registry = Registry(memory_client, container_client)

    self_container = container_client.self_container()

    run_kwargs = {
        'volumes': {mount.source: {'bind': mount.destination} for mount in self_container.mounts},
        'ipc_mode': f"container:{self_container.id}",
        'detach': True,
        'working_dir': DEFAULT_DATA_DIR,
    }

    registry.run_kwargs = run_kwargs

    with open('/pipeline.json') as f:
        pipeline_obj = json.load(f)

    pipeline = oremda.pipeline.deserialize_pipeline(pipeline_obj, memory_client, registry)
    pipeline.run()

    registry.release()
