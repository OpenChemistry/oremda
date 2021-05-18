import numpy as np

from oremda import Client as OremdaClient
from oremda import Pipeline as OremdaPipeline

client = OremdaClient('/run/oremda/plasma.sock')
pipeline = OremdaPipeline(client)

operators = [
    {"name": "view"},
    {
        "name": "multiply",
        "params": {
            "value": 2
        }
    },
    {"name": "view"},
    {
        "name": "add",
        "params": {
            "value": -4
        }
    },
    {"name": "view"},
    {
        "name": "add",
        "params": {
            "value": -3
        }
    },
    {"name": "view"},
]

dtype = np.dtype('int16')
data = np.array([5, 9, 2, 3, 8, 10], dtype=dtype)

output_data = pipeline.run(operators, data)
