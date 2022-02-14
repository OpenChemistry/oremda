import asyncio

from oremda.typing import MPINodeReadyMessage, OperateTaskMessage, Message, MessageType
from oremda.utils.concurrency import ThreadPoolSingleton
from oremda.utils.mpi import mpi_rank

from .event_loop import MPIEventLoop


class MPINonRootEventLoop(MPIEventLoop):
    """Forward messages between the messages queue and MPI nodes"""

    async def loop(self, operator_queue):
        # Use a queue with a rank in order to avoid queue name clashes with
        # rank 0, in case we are running on the same node as rank 0.
        operator_queue_with_rank = f"{operator_queue}_{mpi_rank}"
        while True:
            print(f"{mpi_rank=} Sending ready message for: {operator_queue=}")
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

            task_message = Message(**msg.dict())
            if task_message.type == MessageType.Terminate:
                # If it was a terminate task, send it and finish this node
                print(f"{mpi_rank=} sending terminate task...")
                await self.mqp_send(msg, operator_queue_with_rank)
                print(f"{mpi_rank=} Terminating...")
                # Clean up the operator queue with rank...
                self.mqp_messenger.unlink(operator_queue_with_rank)
                break

            if task_message.type != MessageType.Operate:
                raise NotImplementedError(task_message.type)

            # Add the MPI rank to the output queue to ensure we don't
            # get a name clash with rank 0.
            operate_message = OperateTaskMessage(**msg.dict())
            operate_message.output_queue += f"_{mpi_rank}"

            # Forward to the operator
            print(f"Sending {operate_message} to {operator_queue_with_rank}")
            await self.mqp_send(operate_message, operator_queue_with_rank)

            print(f"MQP message sent to: {operator_queue_with_rank=}")

            result = await self.mqp_recv(operate_message.output_queue)
            print(f"MQP output received: {result=}")

            # Clean up the output queue
            self.mqp_messenger.unlink(operate_message.output_queue)

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
