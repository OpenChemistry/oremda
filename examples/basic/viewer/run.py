import numpy as np

from oremda import Client as OremdaClient
from oremda import Operator as OremdaOperator

class ViewOperator(OremdaOperator):
    def kernel(self, input_data, parameters):
        print("VIEW DATA", input_data, flush=True)

        return input_data


client = OremdaClient('/run/oremda/plasma.sock')

operator = ViewOperator('view', client)
operator.start()
