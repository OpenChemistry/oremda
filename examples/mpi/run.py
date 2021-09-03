#!/usr/bin/env python
import json
import os
from typing import Dict

import matplotlib.pyplot as plt
import numpy as np

from oremda.clients import Client as ContainerClient
from oremda.constants import (
    DEFAULT_PLASMA_SOCKET_PATH,
    DEFAULT_DATA_DIR,
    DEFAULT_OREMDA_VAR_DIR,
)
from oremda.display import DisplayHandle, NoopDisplayHandle
from oremda.event_loops import MPIEventLoop
from oremda.messengers import MPIMessenger, MQPMessenger
from oremda.plasma_client import PlasmaClient
from oremda.registry import Registry
from oremda.typing import (
    ContainerType,
    DisplayType,
    IdType,
    MPINodeReadyMessage,
    OperateTaskMessage,
    Message,
    MessageType,
    Port,
)
from oremda.utils.mpi import mpi_host_name, mpi_rank, mpi_world_size
from oremda.utils.plasma import start_plasma_store
import oremda.pipeline

if mpi_rank == 0:
    print(f"{mpi_world_size=}")

print(f"{mpi_host_name=}, {mpi_rank=}")


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

            # FIXME: why aren't these the same shape?
            y_data = port.data.data[1]
            print(f"{x.shape=}, {y_data.shape=}")
            y = np.zeros(x.shape)
            y[: y_data.shape[0]] = y_data

            label = None
            if port.meta is not None:
                label = port.meta.get("label")

            ax.plot(x, y, label=label)

        ax.legend()
        ax.set(xlabel=x_label, ylabel=y_label)

        fg.savefig(f"/global/u1/p/psavery/data/oremda/{self.id}.png", dpi=fg.dpi)


def display_factory(id: IdType, display_type: DisplayType) -> DisplayHandle:
    if display_type == DisplayType.OneD:
        return MatplotlibDisplayHandle(id)
    else:
        return NoopDisplayHandle(id, display_type)


container_type = ContainerType.Singularity
if "SINGULARITY_BIND" in os.environ:
    # Remove this so we don't repeat the parent container's bind mounting
    del os.environ["SINGULARITY_BIND"]

plasma_kwargs = {
    "memory": 50_000_000,
    "socket_path": DEFAULT_PLASMA_SOCKET_PATH,
}

with start_plasma_store(**plasma_kwargs):
    plasma_client = PlasmaClient(DEFAULT_PLASMA_SOCKET_PATH)
    container_client = ContainerClient(container_type)
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
        "/global/u1/p/psavery/data/oremda": {"bind": DEFAULT_DATA_DIR},
        "/global/u1/p/psavery/virtualenvs/oremda/src/oremda": {"bind": "/oremda"},
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
        future = MPIEventLoop().start_event_loop()

        # Run the pipeline
        print("Running pipeline...")
        pipeline.run()
        print("Releasing registry...")
        registry.release()

        # Wait for the MPIEventLoop to finish
        future.result()
    else:
        registry.start_containers()

        # We currently only support one container per node for rank != 0.
        # Find that image, listen for MPI messages, and forward them.
        image_name = None
        images = registry.images
        for name, image in images.items():
            if image.operator_config.num_containers_on_this_rank > 0:
                image_name = name
                break

        if image_name is None:
            names = list(images.keys())
            msg = f"Could not find image for {mpi_rank=} out of {names}"
            raise Exception(msg)

        operator_name = registry.images[image_name].name
        operator_queue = f"/{operator_name}"
        mpi_messenger = MPIMessenger()
        mqp_messenger = MQPMessenger(plasma_client)
        while True:
            # First, send a message indicating we are ready for input
            ready_msg = MPINodeReadyMessage(
                **{
                    "queue": operator_queue,
                }
            )
            mpi_messenger.send(ready_msg, 0)

            # Now receive a task
            print(f"Waiting to receive MPI task on {mpi_rank=}")
            msg = mpi_messenger.recv(0)
            print(f"MPI message received on {mpi_rank=}, {msg=}")

            local_output_queue = f"/mpi_rank_{mpi_rank}"
            if msg.type == MessageType.Operate:
                operate_message = OperateTaskMessage(**msg.dict())
                # Override the output queue
                output_queue = operate_message.output_queue
                operate_message.output_queue = local_output_queue
                msg = operate_message

                # Tell the operator which mpi rank it is running on
                operate_message.mpi_rank = mpi_rank

            # Forward to the operator
            print(f"Sending {msg} to {operator_queue}")
            mqp_messenger.send(msg, operator_queue)

            print(f"MQP message sent to: {operator_queue=}")

            # If it was a terminate task, finish this node as well
            task_message = Message(**msg.dict())
            if task_message.type == MessageType.Terminate:
                print(f"{mpi_rank=} Terminating...")
                break

            # It must have been an OperateTaskMessage. Receive the output.
            operate_message = OperateTaskMessage(**msg.dict())
            print(f"Receiving output from {local_output_queue}")
            result = mqp_messenger.recv(local_output_queue)
            print(f"MQP output received: {result=}")

            # Forward the result back to the main node
            mpi_messenger.send(result, 0)
            print("MPI message sent back to the main node")
