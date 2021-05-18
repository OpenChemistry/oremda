import numpy as np

from oremda import Client as OremdaClient
from oremda import Operator as OremdaOperator

class MultiplyOperator(OremdaOperator):
    def kernel(self, input_data, parameters):
        value = parameters.get('value', 1)
        output_data = np.ndarray(shape=input_data.shape, dtype=input_data.dtype)
        output_data = input_data * value

        return output_data

client = OremdaClient('/run/oremda/plasma.sock')

operator = MultiplyOperator('multiply', client)
operator.start()
