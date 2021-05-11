import json
import sys

import numpy as np

from oremda import open_memory, open_queue

from_message_queue_name = sys.argv[1]
to_message_queue_name = sys.argv[2]

with open_queue(from_message_queue_name, consume=True) as from_queue:
    message, priority = from_queue.receive()

with open_queue(to_message_queue_name) as to_queue:
    info = json.loads(message)

    shared_memory_name = info['shared_memory_name']
    shape = info['shape']
    dtype = info['dtype']

    with open_memory(shared_memory_name) as shm:
        data = np.ndarray(shape, dtype=np.dtype(dtype), buffer=shm.buf)
        data[:] -= 3
        print('After minus 3, data is:', data)
        to_queue.send(message)
