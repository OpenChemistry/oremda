import asyncio

from oremda.constants import DEFAULT_PLASMA_SOCKET_PATH
from oremda.messengers import MPIMessenger, MQPMessenger
from oremda.plasma_client import PlasmaClient
from oremda.typing import MPINodeReadyMessage, OperateTaskMessage, Message, MessageType
from oremda.utils.asyncio import run_in_executor
from oremda.utils.concurrency import ThreadPoolSingleton
from oremda.utils.mpi import mpi_world_size
from oremda.utils.singleton import Singleton


class MPIEventLoop(Singleton):
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

    async def loop(self, rank):
        while True:
            # Wait until the node indicates it is ready
            msg = await self.mpi_recv(rank)
            ready_msg = MPINodeReadyMessage(**msg.dict())
            queue = ready_msg.queue

            # Wait until a task becomes available for the node
            msg = await self.mqp_recv(queue)
            # Forward the input to the node
            await self.mpi_send(msg, rank)

            # Check if it was a terminate message. If so, we can end our loop.
            task_message = Message(**msg.dict())
            if task_message.type == MessageType.Terminate:
                break

            # It must have been an OperateTaskMessage. Read the output queue.
            operate_message = OperateTaskMessage(**msg.dict())
            output_queue = operate_message.output_queue

            # Get the output from the node
            output = await self.mpi_recv(rank)
            # Put the output on the message queue
            await self.mqp_send(output, output_queue)

    def start_event_loop(self):
        if self.started:
            # Already started...
            return

        def run_loop():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # Use our ThreadPoolExecutor singleton for the asyncio executor
            loop.set_default_executor(ThreadPoolSingleton().executor)

            for i in range(1, mpi_world_size):
                task = loop.create_task(self.loop(i))
                self.tasks.append(task)

            # Run until all tasks complete
            loop.run_until_complete(asyncio.gather(*self.tasks))

        future = ThreadPoolSingleton().submit(run_loop)
        self.started = True
        return future
