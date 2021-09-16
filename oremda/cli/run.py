#!/usr/bin/env python
import json
import os
import click
from typing import cast

from oremda.clients import Client as ContainerClient
from oremda.clients.singularity import SingularityClient
from oremda.clients.docker import DockerClient
from oremda.plasma_client import PlasmaClient
from oremda.registry import Registry
from oremda.constants import (
    DEFAULT_DATA_DIR,
    DEFAULT_OREMDA_VAR_DIR,
)
from oremda.utils.plasma import start_plasma_store
from oremda.typing import ContainerType
from oremda.display import display_factory
import oremda.pipeline


@click.command(
    "run",
    short_help="oremda cli runner",
    help="Run an oremda pipeline on the command line.",
)
@click.argument("pipeline_json", type=click.File("r"))
def main(pipeline_json: click.File):
    if "SINGULARITY_BIND" in os.environ:
        # This means we are running singularity
        container_type = ContainerType.Singularity

        # Remove this so we don't repeat the parent container's bind mounting
        del os.environ["SINGULARITY_BIND"]
    else:
        container_type = ContainerType.Docker

    oremda_var_dir = os.environ.get("OREMDA_VAR_DIR") or DEFAULT_OREMDA_VAR_DIR
    oremda_data_dir = os.environ.get("OREMDA_DATA_DIR") or DEFAULT_DATA_DIR
    plasma_socket_path = f"{oremda_var_dir}/plasma.sock"

    plasma_kwargs = {
        "memory": 50_000_000,
        "socket_path": plasma_socket_path,
    }

    with start_plasma_store(**plasma_kwargs):
        plasma_client = PlasmaClient(plasma_socket_path)
        container_client = ContainerClient(container_type)

        if container_type == ContainerType.Singularity:
            cast(SingularityClient, container_client).images_dir = "/images"

        registry = Registry(plasma_client, container_client)

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
                    "/oremda": {"bind": "/oremda"},
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
            pipeline.run()
        finally:
            registry.release()
