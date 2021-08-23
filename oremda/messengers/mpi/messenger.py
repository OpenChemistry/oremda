from mpi4py import MPI
from pydantic import validate_arguments

from oremda.messengers.base import BaseMessenger

comm = MPI.COMM_WORLD
rank = comm.Get_rank()


class MPIMessenger(BaseMessenger):
    """Message Passing Interface messenger

    Sends a whole dict through MPI via pickling.

    The sender and receiver can be on different nodes.
    """

    @property
    def type(self) -> str:
        return "mpi"

    @validate_arguments
    def send(self, msg: dict, dest: int):
        comm.send(msg, dest=dest)

    @validate_arguments
    def recv(self, source: int) -> dict:
        return comm.recv(source=source)
