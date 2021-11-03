#!/usr/bin/env python
import json
import os
from typing import cast

import click

from oremda.clients import Client as ContainerClient
from oremda.clients.docker import DockerClient
from oremda.clients.singularity import SingularityClient
from oremda.constants import (
    DEFAULT_DATA_DIR,
    DEFAULT_OREMDA_VAR_DIR,
)
from oremda.display import display_factory
from oremda.event_loops import MPINonRootEventLoop, MPIRootEventLoop
from oremda.plasma_client import PlasmaClient
from oremda.registry import Registry
from oremda.typing import ContainerType
from oremda.utils.mpi import mpi_rank, mpi_world_size
from oremda.utils.plasma import start_plasma_store
import oremda.pipeline


@click.command(
    "run",
    short_help="oremda cli runner",
    help="Run an oremda pipeline on the command line.",
)
@click.argument("pipeline_json", type=click.File("r"))
def main(pipeline_json: click.File):

    if os.environ.get("SINGULARITY_CONTAINER") and "SINGULARITY_BIND" in os.environ:
        # The runner is in a singularity container.
        # Avoid repeating the runner bindings for the operators.
        del os.environ["SINGULARITY_BIND"]

    container_types = {
        "docker": ContainerType.Docker,
        "singularity": ContainerType.Singularity,
    }

    container_type_env = os.environ.get("OREMDA_CONTAINER_TYPE", "docker")
    if container_type_env not in container_types:
        raise NotImplementedError(container_type_env)

    container_type = container_types[container_type_env]

    oremda_var_dir = os.environ.get("OREMDA_VAR_DIR") or DEFAULT_OREMDA_VAR_DIR
    oremda_data_dir = os.environ.get("OREMDA_DATA_DIR") or DEFAULT_DATA_DIR
    sif_dir = os.environ.get("OREMDA_SIF_DIR", "/images")
    plasma_memory = int(os.environ.get("OREMDA_PLASMA_MEMORY", 50_000_000))
    operator_config_file = os.environ.get("OREMDA_OPERATOR_CONFIG_FILE")
    plasma_socket_path = f"{oremda_var_dir}/plasma.sock"

    plasma_kwargs = {
        "memory": plasma_memory,
        "socket_path": plasma_socket_path,
    }

    with start_plasma_store(**plasma_kwargs):
        plasma_client = PlasmaClient(plasma_socket_path)
        container_client = ContainerClient(container_type)

        if container_type == ContainerType.Singularity:
            cast(SingularityClient, container_client).images_dir = sif_dir

        registry_kwargs = {
            "plasma_client": plasma_client,
            "container_client": container_client,
            "operator_config_file": operator_config_file,
        }
        registry = Registry(**registry_kwargs)
        future = None

        try:
            run_kwargs = {
                "detach": True,
                "working_dir": DEFAULT_DATA_DIR,
            }

            if container_type == ContainerType.Singularity:
                # The mounts in singularity child containers refer to the
                # parent container's directories.
                volumes = {
                    oremda_var_dir: {"bind": DEFAULT_OREMDA_VAR_DIR},
                    oremda_data_dir: {"bind": DEFAULT_DATA_DIR},
                }
                run_kwargs["volumes"] = volumes
            if container_type == ContainerType.Docker:
                # The mounts in docker "sibling" containers refer to the
                # host directories.
                self_container = cast(DockerClient, container_client).self_container()

                # Is the runner in a container itself or bare metal?
                if self_container is None:
                    volumes = {
                        oremda_var_dir: {"bind": DEFAULT_OREMDA_VAR_DIR},
                        oremda_data_dir: {"bind": DEFAULT_DATA_DIR},
                    }
                    run_kwargs["volumes"] = volumes
                    run_kwargs["ipc_mode"] = "host"
                else:
                    volumes = {
                        mount.source: {"bind": mount.destination}
                        for mount in self_container.mounts
                    }
                    run_kwargs["volumes"] = volumes

                    # Get the child containers to share IPC with the parent
                    run_kwargs["ipc_mode"] = f"container:{self_container.id}"

            registry.run_kwargs = run_kwargs

            pipeline_obj = json.loads(pipeline_json.read())  # type: ignore

            pipeline = oremda.pipeline.deserialize_pipeline(
                pipeline_obj, plasma_client, registry, display_factory
            )

            if mpi_rank == 0:
                if mpi_world_size > 1:
                    future = MPIRootEventLoop().start_event_loop()

                pipeline.run()
            else:
                registry.start_containers()
                future = MPINonRootEventLoop().start_event_loop(registry)
                # Wait for the event loop to finish
                future.result()
        finally:
            if mpi_rank == 0:
                registry.release()

                if mpi_world_size > 1 and future is not None:
                    # Wait for the event loop to finish
                    future.result()
