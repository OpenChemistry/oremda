#!/usr/bin/env python
import json
import os
import click

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
from oremda.display import display_factory
import oremda.pipeline


@click.command(
    "run",
    short_help="oremda cli runner",
    help="Run an oremda pipeline on the command line.",
)
@click.argument("pipeline", type=click.Path(exists=True, dir_okay=False))
def main(pipeline):
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

        if container_type == ContainerType.Singularity:
            container_client.images_dir = "/images"

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
                mount.source: {"bind": mount.destination}
                for mount in self_container.mounts
            }
            run_kwargs["volumes"] = volumes

            # Get the child containers to share IPC with the parent
            run_kwargs["ipc_mode"] = f"container:{self_container.id}"

        registry.run_kwargs = run_kwargs

        with open(pipeline) as f:
            pipeline_obj = json.load(f)

        pipeline = oremda.pipeline.deserialize_pipeline(
            pipeline_obj, plasma_client, registry, display_factory
        )

        try:
            pipeline.run()
        finally:
            registry.release()
