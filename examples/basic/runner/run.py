#!/usr/bin/env python
import json
import os
from typing import Dict

import matplotlib.pyplot as plt

from oremda.clients import Client as ContainerClient
from oremda.plasma_client import PlasmaClient
from oremda.registry import Registry
from oremda.constants import (
    DEFAULT_PLASMA_SOCKET_PATH,
    DEFAULT_DATA_DIR,
    DEFAULT_OREMDA_VAR_DIR,
)
from oremda.utils.plasma import start_plasma_store
from oremda.typing import ContainerType, DisplayType, IdType, Port
from oremda.display import DisplayFactory, DisplayHandle, NoopDisplayHandle
import oremda.pipeline


class MatplotlibDisplayHandle(DisplayHandle):
    def __init__(self, id: IdType):
        super().__init__(id, DisplayType.OneD)
        self.inputs: Dict[IdType, Port] = {}

    def add(self, sourceId: IdType, input: Port):
        self.inputs[sourceId] = input
        self.render()

    def remove(self, sourceId: IdType):
        if id in self.inputs:
            del self.inputs[sourceId]
        self.render()

    def clear(self):
        self.inputs = {}
        self.render()

    def render(self):
        x_label = self.parameters.get("xLabel", "x")
        y_label = self.parameters.get("yLabel", "y")

        fg, ax = plt.subplots(1, 1)

        for port in self.inputs.values():
            if port.data is None:
                continue

            x = port.data.data[0]
            y = port.data.data[1]

            label = None
            if port.meta is not None:
                label = port.meta.get('label')

            ax.plot(x, y, label=label)

        ax.legend()
        ax.set(xlabel=x_label, ylabel=y_label)

        fg.savefig(f"/data/{self.id}.png", dpi=fg.dpi)


def display_factory(id: IdType, display_type: DisplayType) -> DisplayHandle:
    if display_type == DisplayType.OneD:
        return MatplotlibDisplayHandle(id)
    else:
        return NoopDisplayHandle(id, display_type)


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
        "detach": True,
        "working_dir": DEFAULT_DATA_DIR,
    }

    if container_type == ContainerType.Singularity:
        # The mounts in singularity child containers refer to the
        # parent container's directories.
        volumes = {
            DEFAULT_OREMDA_VAR_DIR: {"bind": DEFAULT_OREMDA_VAR_DIR},
            DEFAULT_DATA_DIR: {"bind": DEFAULT_DATA_DIR},
            "/oremda": {"bind": "/oremda"},
        }
        run_kwargs["volumes"] = volumes
    if container_type == ContainerType.Docker:
        # The mounts in docker "sibling" containers refer to the
        # host directories.
        self_container = container_client.self_container()
        volumes = {
            mount.source: {"bind": mount.destination} for mount in self_container.mounts
        }
        run_kwargs["volumes"] = volumes

        # Get the child containers to share IPC with the parent
        run_kwargs["ipc_mode"] = f"container:{self_container.id}"

    registry.run_kwargs = run_kwargs

    with open("/runner/pipeline.json") as f:
        pipeline_obj = json.load(f)

    pipeline = oremda.pipeline.deserialize_pipeline(
        pipeline_obj, plasma_client, registry, display_factory
    )

    try:
        pipeline.run()
    finally:
        registry.release()
