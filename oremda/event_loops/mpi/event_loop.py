from abc import ABC, abstractmethod

from oremda.constants import DEFAULT_PLASMA_SOCKET_PATH
from oremda.messengers import MPIMessenger, MQPMessenger
from oremda.plasma_client import PlasmaClient
from oremda.utils.asyncio import run_in_executor
from oremda.utils.singleton import SingletonMetaclass


class MPIEventLoop(ABC, metaclass=SingletonMetaclass):
    """Forward messages between the messages queue and MPI nodes"""

    def __init__(self):
        self.client = PlasmaClient(DEFAULT_PLASMA_SOCKET_PATH)
        self.mpi_messenger = MPIMessenger()
        self.mqp_messenger = MQPMessenger(self.client)
        self.tasks = []
        self.started = False

    @run_in_executor
    def mpi_send(self, msg, dest):
        return self.mpi_messenger.send(msg, dest)

    @run_in_executor
    def mpi_recv(self, source):
        return self.mpi_messenger.recv(source)

    @run_in_executor
    def mqp_send(self, msg, dest):
        return self.mqp_messenger.send(msg, dest)

    @run_in_executor
    def mqp_recv(self, source):
        return self.mqp_messenger.recv(source)

    @abstractmethod
    async def loop(self):
        pass

    @abstractmethod
    def start_event_loop(self):
        pass
