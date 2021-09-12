import asyncio

from oremda.typing import MPINodeReadyMessage, OperateTaskMessage, Message, MessageType
from oremda.utils.concurrency import ThreadPoolSingleton
from oremda.utils.mpi import mpi_rank

from .event_loop import MPIEventLoop


class MPINonRootEventLoop(MPIEventLoop):
    """Forward messages between the messages queue and MPI nodes"""

    async def loop(self, operator_queue):
        while True:
            # First, send a message indicating we are ready for input
            ready_msg = MPINodeReadyMessage(
                **{
                    "queue": operator_queue,
                }
            )
            await self.mpi_send(ready_msg, 0)

            # Now receive a task
            print(f"Waiting to receive MPI task on {mpi_rank=}")
            msg = await self.mpi_recv(0)
            print(f"MPI message received on {mpi_rank=}, {msg=}")

            # Forward to the operator
            print(f"Sending {msg} to {operator_queue}")
            await self.mqp_send(msg, operator_queue)

            print(f"MQP message sent to: {operator_queue=}")

            # If it was a terminate task, finish this node as well
            task_message = Message(**msg.dict())
            if task_message.type == MessageType.Terminate:
                print(f"{mpi_rank=} Terminating...")
                break

            # It must have been an OperateTaskMessage. Receive the output.
            operate_message = OperateTaskMessage(**msg.dict())
            output_queue = operate_message.output_queue
            result = await self.mqp_recv(output_queue)
            print(f"MQP output received: {result=}")

            # Forward the result back to the main node
            await self.mpi_send(result, 0)
            print("MPI message sent back to the main node")

    def start_event_loop(self, registry):
        if self.started:
            # Already started...
            return

        def run_loop():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # Use our ThreadPoolExecutor singleton for the asyncio executor
            loop.set_default_executor(ThreadPoolSingleton().executor)

            # We currently only support one container per node for rank != 0.
            # Find that image, listen for MPI messages, and forward them.
            image_name = None
            images = registry.images
            for name, image in images.items():
                if image.operator_config.num_containers_on_this_rank > 0:
                    image_name = name
                    break

            if image_name is None:
                names = list(images.keys())
                msg = f"Could not find image for {mpi_rank=} out of {names}"
                raise Exception(msg)

            operator_name = registry.images[image_name].name
            operator_queue = f"/{operator_name}"

            task = loop.create_task(self.loop(operator_queue))
            self.tasks.append(task)

            # Run until all tasks complete
            loop.run_until_complete(asyncio.gather(*self.tasks))

        future = ThreadPoolSingleton().submit(run_loop)
        self.started = True
        return future
