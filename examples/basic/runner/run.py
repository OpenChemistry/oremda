#!/usr/bin/env python
import os
import json
from oremda.clients import Client as ContainerClient
from oremda.shared_resources import Client as MemoryClient
from oremda.registry import Registry
from oremda.constants import DEFAULT_PLASMA_SOCKET_PATH
import oremda.pipeline

memory_client = MemoryClient(DEFAULT_PLASMA_SOCKET_PATH)
container_client = ContainerClient('docker')

registry = Registry(memory_client, container_client)

self_attrs = container_client.client.containers.get(os.environ.get('HOSTNAME')).attrs
ipc_mode = self_attrs['HostConfig']['IpcMode']

run_kwargs = {
    'volumes': {
        '/run/oremda': {
            'bind': '/run/oremda',
        },
        '/home/alessandro/oremda_data': {
            'bind': '/data',
        },
    },
    'ipc_mode': ipc_mode,
    'detach': True,
    'working_dir': '/data',
}

registry.run_kwargs = run_kwargs

with open('/pipeline.json') as f:
    pipeline_obj = json.load(f)

pipeline = oremda.pipeline.deserialize_pipeline(pipeline_obj, memory_client, registry)
pipeline.run()

registry.release()
