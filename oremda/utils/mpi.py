import os

# Constants
OREMDA_MPI_RANK_ENV_VAR = "OREMDA_MPI_RANK"

try:
    from mpi4py import MPI
except ImportError:
    import socket

    comm = None
    rank = 0
    world_size = 1
    host_name = socket.gethostname()
    query_thread = -1
else:
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    world_size = comm.Get_size()
    host_name = MPI.Get_processor_name()
    query_thread = MPI.Query_thread()

mpi_comm = comm
mpi_rank = rank
mpi_world_size = world_size
mpi_host_name = host_name

if env_rank := os.environ.get(OREMDA_MPI_RANK_ENV_VAR):
    # Override the MPI rank with what was provided in the environment
    mpi_rank = int(env_rank)


def query_thread_to_string(query_thread):
    if query_thread == -1:
        return

    options = {
        MPI.THREAD_SINGLE: "MPI_THREAD_SINGLE",
        MPI.THREAD_FUNNELED: "MPI_THREAD_FUNNELED",
        MPI.THREAD_SERIALIZED: "MPI_THREAD_SERIALIZED",
        MPI.THREAD_MULTIPLE: "MPI_THREAD_MULTIPLE",
    }

    if query_thread not in options:
        raise Exception(f"Unknown level of thread support: {query_thread}")

    return options[query_thread]


mpi_thread_support = query_thread_to_string(query_thread)
