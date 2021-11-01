from oremda.utils.mpi import OREMDA_MPI_RANK_ENV_VAR, mpi_rank  # noqa: F401

if mpi_rank == 0:
    _plasma_sock = "plasma.sock"
else:
    _plasma_sock = f"plasma_{mpi_rank}.sock"

DEFAULT_OREMDA_VAR_DIR = "/tmp"
DEFAULT_PLASMA_SOCKET_PATH = f"{DEFAULT_OREMDA_VAR_DIR}/{_plasma_sock}"
DEFAULT_DATA_DIR = "/data"
OREMDA_DOCKER_ORG = "oremda"
OREMDA_IMAGE_LABEL_NAME = "oremda.name"
OREMDA_SIF_GLOB_PATTERN = "oremda_*.sif"
SINGULARITY_FROM_LABEL = "org.label-schema.usage.singularity.deffile.from"
