import asyncio

from oremda.typing import MPINodeReadyMessage, OperateTaskMessage, Message, MessageType
from oremda.utils.concurrency import ThreadPoolSingleton
from oremda.utils.mpi import mpi_world_size

from .event_loop import MPIEventLoop


class MPIRootEventLoop(MPIEventLoop):
    """Forward messages between the messages queue and MPI nodes"""

    async def loop(self, rank):
        while True:
            # Wait until the node indicates it is ready
            print(f"Waiting for {rank=} to be ready...")
            msg = await self.mpi_recv(rank)
            print(f"Received message from {rank=}!")
            ready_msg = MPINodeReadyMessage(**msg.dict())
            queue = ready_msg.queue
            print(f"{rank=} is ready! queue is {queue}. Waiting for input...")

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
