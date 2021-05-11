import json
import sys

import numpy as np

from oremda import open_memory, open_queue
from oremda.constants import OREMDA_FINISHED_QUEUE

from_message_queue_name = sys.argv[1]

with open_queue(from_message_queue_name, consume=True) as from_queue:
    message, priority = from_queue.receive()

info = json.loads(message)

shared_memory_name = info['shared_memory_name']
shape = info['shape']
dtype = info['dtype']

with open_memory(shared_memory_name, consume=True) as shm:
    data = np.ndarray(shape, dtype=np.dtype(dtype), buffer=shm.buf)
    print('In viewer, data is:', data)


# Tell the loader it can shut down
with open_queue(OREMDA_FINISHED_QUEUE) as finished_queue:
    print('sending finished signal from viewer')
    finished_dict = {
        'message': 'Success!',
        'status': str(0),
    }
    finished_queue.send(json.dumps(finished_dict))
