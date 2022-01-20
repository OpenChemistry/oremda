import click
import requests
import docker
from typing import Dict, List
from spython.main import Client as sclient

from oremda.constants import OREMDA_DOCKER_ORG
from . import logger

SREGISTRY_API_URL = "https://library.sylabs.io/v1"


def _fetch_oremda_sregistry_collection_id() -> str:
    r = requests.get(f"{SREGISTRY_API_URL}/collections/oremda/oremda")
    r.raise_for_status()

    return r.json()["data"]["id"]


def _fetch_sregistry_collection_containers(collection_id: str) -> Dict:
    r = requests.get(f"{SREGISTRY_API_URL}/collections/{collection_id}/_containers")
    r.raise_for_status()

    return r.json()["data"]


def _fetch_sregistry_collection_container(uri: str, container_dir) -> None:
    sclient.pull(image=uri, pull_folder=container_dir, force=True)


def _fetch_all_sregistry_containers(container_dir):
    collection_id = _fetch_oremda_sregistry_collection_id()

    for container in _fetch_sregistry_collection_containers(collection_id):

        name = container["name"]
        tags = container["imageTags"]
        tag = "latest"

        if "latest" not in tags:
            tag = tags.keys()[0]
            logger.warn(
                "Container '{name}' doesn't have a latest tag, pull '{tag}' instead."
            )

        uri = f"library://oremda/oremda/{name}:{tag}"

        logger.info(f"Pulling singularity container '{name}:{tag}'.")

        _fetch_sregistry_collection_container(uri, container_dir)


def _fetch_dockerhub_image_names(client) -> List[str]:
    images = []
    for image in client.images.search(term="oremda"):
        image_name = image["name"]
        if not image_name.startswith(f"{OREMDA_DOCKER_ORG}/"):
            continue

        images.append(image_name)

    return images


def _fetch_all_dockerhub_images(client):
    for image_name in _fetch_dockerhub_image_names(client):
        logger.info(f"Pulling docker image '{image_name}:latest'.")
        client.images.pull(image_name, "latest")


@click.command(
    "pull",
    short_help="oremda pull",
    help="Pull all available oremda operators.",
)
@click.option(
    "--type",
    "container_type",
    default="docker",
    type=click.Choice(["docker", "singularity"]),
)
@click.option(
    "--dir",
    "image_dir",
    envvar="OREMDA_SINGULARITY_IMAGE_DIR:",
    type=click.Path(exists=True),
)
def main(container_type, image_dir):
    if container_type == "singularity":
        _fetch_all_sregistry_containers(str(image_dir))
    elif container_type == "docker":
        client = docker.from_env()  # type: ignore
        _fetch_all_dockerhub_images(client)
