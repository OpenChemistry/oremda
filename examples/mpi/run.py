#!/usr/bin/env python
import json
import os
from typing import Dict

import matplotlib.pyplot as plt

from oremda.constants import (
    DEFAULT_PLASMA_SOCKET_PATH,
    DEFAULT_DATA_DIR,
    DEFAULT_OREMDA_VAR_DIR,
)
from oremda.display import DisplayHandle, NoopDisplayHandle
from oremda.event_loops import MPINonRootEventLoop, MPIRootEventLoop
from oremda.plasma_client import PlasmaClient
from oremda.registry import Registry
from oremda.typing import (
    DisplayType,
    IdType,
    Port,
)
from oremda.utils.mpi import mpi_host_name, mpi_rank, mpi_world_size
from oremda.utils.plasma import start_plasma_store
from oremda.clients.singularity.client import SingularityClient
import oremda.pipeline

if mpi_rank == 0:
    print(f"{mpi_world_size=}")

print(f"{mpi_host_name=}, {mpi_rank=}")

home_dir = os.getenv("HOME")


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
                label = port.meta.get("label")

            ax.plot(x, y, label=label)

        ax.legend()
        ax.set(xlabel=x_label, ylabel=y_label)

        fg.savefig(f"{home_dir}/data/oremda/{self.id}.png", dpi=fg.dpi)


def display_factory(id: IdType, display_type: DisplayType) -> DisplayHandle:
    if display_type == DisplayType.OneD:
        return MatplotlibDisplayHandle(id)
    else:
        return NoopDisplayHandle(id, display_type)


if "SINGULARITY_BIND" in os.environ:
    # Remove this so we don't repeat the parent container's bind mounting
    del os.environ["SINGULARITY_BIND"]

plasma_kwargs = {
    "memory": 50_000_000,
    "socket_path": DEFAULT_PLASMA_SOCKET_PATH,
}

with start_plasma_store(**plasma_kwargs):
    plasma_client = PlasmaClient(DEFAULT_PLASMA_SOCKET_PATH)
    container_client = SingularityClient()
    container_client.images_dir = "images"

    operator_config_file = "operator_config.json"
    registry = Registry(plasma_client, container_client, operator_config_file)

    run_kwargs = {
        "detach": True,
        "working_dir": DEFAULT_DATA_DIR,
    }

    # The mounts in singularity child containers refer to the
    # parent container's directories.
    volumes = {
        DEFAULT_OREMDA_VAR_DIR: {"bind": DEFAULT_OREMDA_VAR_DIR},
        f"{home_dir}/data/oremda": {"bind": DEFAULT_DATA_DIR},
        f"{home_dir}/virtualenvs/oremda/src/oremda": {"bind": "/oremda"},
    }
    run_kwargs["volumes"] = volumes

    registry.run_kwargs = run_kwargs

    with open("pipeline.json") as f:
        pipeline_obj = json.load(f)

    pipeline = oremda.pipeline.deserialize_pipeline(
        pipeline_obj, plasma_client, registry, display_factory
    )

    if mpi_rank == 0:
        print("Starting event loop...")
        # Start the MPI event loop
        future = MPIRootEventLoop().start_event_loop()

        # Run the pipeline
        print("Running pipeline...")
        pipeline.run()
        print("Releasing registry...")
        registry.release()

        # Wait for the event loop to finish
        future.result()
    else:
        registry.start_containers()

        future = MPINonRootEventLoop().start_event_loop(registry)

        # Wait for the event loop to finish
        future.result()
