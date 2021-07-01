import numpy as np

import json

from oremda import Client as OremdaClient
import oremda.pipeline
from oremda.constants import DEFAULT_PLASMA_SOCKET_PATH
from oremda.utils.plasma import start_plasma_store

with open('/pipeline.json') as f:
    pipeline_obj = json.load(f)

kwargs = {
    'memory': 50000000,
    'socket_path': DEFAULT_PLASMA_SOCKET_PATH,
}

with start_plasma_store(**kwargs):
    client = OremdaClient(DEFAULT_PLASMA_SOCKET_PATH)

    pipeline = oremda.pipeline.deserialize_pipeline(pipeline_obj, client)
    pipeline.run()
