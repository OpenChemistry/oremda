import json
import sys

import numpy as np

from oremda import open_memory, open_queue
from oremda.constants import OREMDA_FINISHED_QUEUE

to_message_queue_name = sys.argv[1]
queues_to_create = sys.argv[2:]

shared_memory_name = 'data'
dtype = np.dtype('uint16')
array_shape = (6,)
total_size = dtype.itemsize * np.prod(array_shape)

with open_queue(to_message_queue_name, create=True) as to_queue:
    with open_memory(shared_memory_name, create=True, size=total_size) as shm:
        data = np.ndarray(array_shape, dtype=dtype, buffer=shm.buf)
        data[:] = [5, 9, 2, 3, 8, 7]

        print('Loaded data is:', data)

        info = {
            'shared_memory_name': shared_memory_name,
            'shape': data.shape,
            'dtype': str(data.dtype),
        }

        to_queue.send(json.dumps(info))


# Create any additional queues that we were asked to create
for name in queues_to_create:
    with open_queue(name, create=True):
        pass

# The loader hosts the ipc shared memory and queues, so we need
# to keep it running until everything is finished.
# Wait until we receive a message from the finished queue to close.
kwargs = {
    'name': OREMDA_FINISHED_QUEUE,
    'create': True,
    'consume': True,
}
with open_queue(**kwargs) as finished_queue:
    print('Loader finished. Waiting for finished signal...')
    message, priority = finished_queue.receive()
    print('Finished signal received!')
