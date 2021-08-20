#!/usr/bin/env python
import json
import os

from oremda.clients import Client as ContainerClient
from oremda.constants import (
    DEFAULT_PLASMA_SOCKET_PATH,
    DEFAULT_DATA_DIR,
    DEFAULT_OREMDA_VAR_DIR,
)
from oremda.messengers import MPIMessenger, MQPMessenger
from oremda.plasma_client import PlasmaClient
from oremda.registry import Registry
from oremda.typing import ContainerType, OperateTaskMessage, TaskMessage, TaskType
from oremda.utils.mpi import mpi_rank
from oremda.utils.plasma import start_plasma_store
import oremda.pipeline

print(f"{mpi_rank=}")

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
        pipeline_obj, plasma_client, registry
    )
    if mpi_rank == 0:
        pipeline.run()
        registry.release()
    else:
        container = registry.run_image_for_rank()

        # Listen for MPI messages and forward them to the image
        image_name = registry.image_for_rank
        operator_name = registry.images[image_name].name
        operator_queue = f"/{operator_name}"
        mpi_messenger = MPIMessenger()
        mqp_messenger = MQPMessenger(plasma_client)
        while True:
            msg = mpi_messenger.recv(0)
            print(f"MPI message received on {mpi_rank=}, {msg=}")

            # Forward to the operator
            mqp_messenger.send(msg, operator_queue)

            print(f"MQP message sent to: {operator_queue=}")

            # If it was a terminate task, finish this node as well
            task_message = TaskMessage(**msg)
            if task_message.task == TaskType.Terminate:
                print(f"{mpi_rank=} Terminating...")
                break

            # It must have been an OperateTaskMessage. Receive the output.
            operate_message = OperateTaskMessage(**msg)
            result = mqp_messenger.recv(operate_message.output_queue)
            print(f"MQP output received: {result=}")

            # Forward the result back to the main node
            mpi_messenger.send(result, 0)
            print("MPI message sent back to the main node")
