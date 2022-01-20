from oremda.utils.mpi import mpi_thread_support

from .thread_multiple import MPIThreadMultipleImplementation
from .thread_serial import MPIThreadSerialImplementation

implementations = {
    "MPI_THREAD_SERIALIZED": MPIThreadSerialImplementation,
    "MPI_THREAD_MULTIPLE": MPIThreadMultipleImplementation,
}

if mpi_thread_support not in implementations:
    raise NotImplementedError(mpi_thread_support)

MPIMessengerImplementation = implementations[mpi_thread_support]  # type: ignore
