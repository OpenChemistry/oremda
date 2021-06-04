from pathlib import Path
from threading import Lock

from spython.main import Client as client

from oremda.utils.concurrency import ThreadPoolSingleton
from oremda.clients.base import ClientBase, ContainerBase


class SingularityClient(ClientBase):

    @property
    def client(self):
        return client

    @property
    def type(self):
        return 'singularity'

    def run(self, image, *args, **kwargs):
        kwargs = self._docker_kwargs_to_singularity(kwargs)

        name = Path(image).stem
        options = kwargs.get('options')
        container = SingularityContainer(image, name, options=options)

        if args:
            container.run(*args, **kwargs)

        return container

    def _docker_kwargs_to_singularity(self, kwargs):
        # This converts docker-style kwargs to singularity
        ret = {}
        options = []
        if not kwargs.get('detach', False):
            msg = 'Detach mode is currently required for singularity'
            raise Exception(msg)

        if 'ipc_mode' in kwargs:
            print('Warning: IPC mode will be ignored for singularity')

        if 'volumes' in kwargs:
            volumes = kwargs['volumes']
            for key, val in volumes.items():
                bind = val['bind']
                options += ['--bind', f'{key}:{bind}']

        ret['options'] = options
        return ret


class SingularityContainer(ContainerBase):

    def __init__(self, image, name=None, options=None):
        self.instance = client.instance(image, name=name, options=options)
        self._logs_lock = Lock()
        self._logs = []
        self._stream_command = None

    @property
    def id(self):
        return self.instance.name

    def __del__(self):
        self.stop()

    def run(self, *args, **kwargs):
        if self._stream_command is not None:
            msg = f'A command is already in instance {self.instance.name}'
            raise Exception(msg)

        # Clear the logs
        with self._logs_lock:
            self._logs.clear()

        # Always stream
        kwargs = kwargs.copy()
        kwargs['stream'] = True

        self._stream_command = client.run(self.instance, *args, **kwargs)

        # Append to the logs in a background thread
        ThreadPoolSingleton().submit(self._read_logs)

    def _read_logs(self):
        # This function should run in a background thread
        if not self._stream_command:
            return

        for output in self._stream_command:
            with self._logs_lock:
                self._logs.append(output)

        self._stream_command = None

    def logs(self, *args, **kwargs):
        with self._logs_lock:
            return ''.join(self._logs)

    def stop(self, *args, **kwargs):
        instance_names = [x.name for x in client.instances()]
        if self.instance.name not in instance_names:
            # It isn't running
            return

        self.instance.stop()

    def remove(self, *args, **kwargs):
        self.stop()
