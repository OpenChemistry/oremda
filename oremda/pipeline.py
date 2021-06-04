import json

import pyarrow.plasma as plasma
from oremda.constants import OREMDA_FINISHED_QUEUE


class Pipeline:
    def __init__(self, client):
        self.client = client

    def run(self, operators, input_data):
        self._create_queues(operators)
        self._spawn_containers(operators)

        object_id = self.client.create_object(input_data)

        for operator in operators:
            name = operator.get('name')
            params = operator.get('params')
            op_queue_name = f'/{name}'

            with self.client.open_queue(op_queue_name) as op_queue:
                info = {
                   'object_id': object_id.binary().hex(),
                   'params': params
                }

                op_queue.send(json.dumps(info))

            with self.client.open_queue(OREMDA_FINISHED_QUEUE) as done_queue:
                message, priority = done_queue.receive()

                info = json.loads(message)

                object_id = plasma.ObjectID(bytes.fromhex(info.get('object_id')))

        self._terminate_operators(operators)
        # with self.client.open_queue(OREMDA_FINISHED_QUEUE, consume=True) as done_queue:
        #     pass

        return self.client.get_object(object_id)

    def _terminate_operators(self, operators):
        message = json.dumps({'task': 'terminate'})
        names = set(x['name'] for x in operators)
        for name in names:
            with self.client.open_queue(f'/{name}') as queue:
                queue.send(message)

    def _create_queues(self, operators):
        with self.client.open_queue(OREMDA_FINISHED_QUEUE, create=True, reuse=True) as done_queue:
            pass

        for operator in operators:
            name = operator.get('name')
            op_queue_name = f'/{name}'

            with self.client.open_queue(op_queue_name, create=True, reuse=True) as op_queue:
                pass

    def _spawn_containers(self, operators):
        pass
