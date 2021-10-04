from mpi4py import MPI

from oremda.utils.singleton import Singleton

comm = MPI.COMM_WORLD


class MPIThreadMultipleImplementation(Singleton):
    """This class just sends and receives the messages via MPI

    This class is designed to be used on a system with a level of thread
    support of MPI_THREAD_MULTIPLE.

    Since multi-threading is supported, we can just send and recv messages
    right away, no matter what thread we are on.
    """

    def send(self, msg: dict, dest: int):
        comm.send(msg, dest=dest)

    def recv(self, source: int) -> dict:
        return comm.recv(source=source)
