import json
from typing import Dict

from oremda.typing import TerminateTaskMessage

class Registry:
    def __init__(self, memory_client, container_client):
        self.memory_client = memory_client
        self.container_client = container_client
        self.images = {}
        self.run_kwargs = {}

    def _inspect(self, image_name):
        image = self.container_client.image(image_name)

        labels = image.oremda_labels

        ports = labels.setdefault('ports', {})
        ports.setdefault('input', {})
        ports.setdefault('output', {})

        name = labels.get('name')

        assert(name is not None)

        return labels

    def _info(self, image_name):
        info = self.images.get(image_name)
        if info is None:
            labels = self._inspect(image_name)
            info = {
                'labels': labels,
                'container': None
            }
            self.images[image_name] = info

        return info

    def name(self, image_name):
        info = self._info(image_name)
        return info['labels']['name']

    def ports(self, image_name):
        info = self._info(image_name)
        return info['labels']['ports']

    def params(self, image_name):
        info = self._info(image_name)
        return info['labels']['params']

    def running(self, image_name):
        info = self._info(image_name)
        return info['container'] is not None

    def run(self, image_name,):
        info = self._info(image_name)
        container = info['container']
        if container is None:
            try:
                container = self.container_client.run(image_name, **self.run_kwargs)
                info['container'] = container
            except Exception as e:
                print(f'An exception was caught: {e}')
                if container is not None:
                    print('Logs:', container.logs())
                raise

        return container

    def stop(self, image_name):
        if not self.running(image_name):
            return

        queue_name = self.name(image_name)
        message = json.dumps(TerminateTaskMessage().dict())
        with self.memory_client.open_queue(f'/{queue_name}') as queue:
            queue.send(message)

    def release(self):
        for image_name in self.images:
            self.stop(image_name)
