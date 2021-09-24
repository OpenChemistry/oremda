from typing import Dict

import numpy as np

from oremda import operator
from oremda.typing import JSONType, PortKey, RawPort


@operator
def fft2d(
    inputs: Dict[PortKey, RawPort], parameters: JSONType
) -> Dict[PortKey, RawPort]:

    data = inputs["in"].data

    if data is None:
        raise Exception("Missing input data")

    data_g = np.fft.fft2(data)

    outputs = {
        "real": RawPort(meta=inputs["in"].meta, data=data_g.real),
        "imag": RawPort(meta=inputs["in"].meta, data=data_g.imag),
    }

    return outputs
