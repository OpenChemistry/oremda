from threading import Lock

from spython.main import Client as client

from oremda.utils.concurrency import ThreadPoolSingleton
from oremda.clients.base import ContainerBase


class SingularityContainer(ContainerBase):
    def __init__(self, image, name=None):
        self.image = image
        self.name = name

        self._logs_lock = Lock()
        self._logs = []
        self._stream_command = None
        self.future = None

    @property
    def id(self):
        return self.name

    def __del__(self):
        self.stop()

    def run(self, *args, **kwargs):
        if self._stream_command is not None:
            msg = f"A command is already running for {self.id}"
            raise Exception(msg)

        # Clear the logs
        with self._logs_lock:
            self._logs.clear()

        # Run in a background thread
        self.future = ThreadPoolSingleton().submit(self._run, *args, **kwargs)

    def _run(self, *args, **kwargs):
        # This function should run in a background thread

        kwargs = kwargs.copy()
        kwargs["image"] = self.image

        # Always stream
        kwargs["stream"] = True

        # spython will error if we don't return the result...
        kwargs["return_result"] = True

        self._stream_command = client.run(**kwargs)

        # Write logs as they come in
        for output in self._stream_command:
            with self._logs_lock:
                self._logs.append(output)

        self._stream_command = None

    def logs(self, *args, **kwargs):
        with self._logs_lock:
            return "".join(self._logs)

    def stop(self, *args, **kwargs):
        # We cannot force kill the singularity containers right now,
        # mostly because the singularity api doesn't give us a way to
        # kill the singularity subprocess. We may need to call subprocess
        # ourselves if we need to force kill the singularity subprocess in
        # the future.

        # Instead, wait for the future to finish
        self.wait()

    def remove(self, *args, **kwargs):
        self.stop()

    def wait(self, *args, **kwargs):
        if self.future is None:
            # No process to wait on
            return

        self.future.result()
        self.future = None
