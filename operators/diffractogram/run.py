from typing import Dict

import numpy as np

from oremda.api import operator
from oremda.typing import JSONType, PortKey, RawPort


@operator
def diffractogram(
    inputs: Dict[PortKey, RawPort], parameters: JSONType
) -> Dict[PortKey, RawPort]:

    image = inputs["image"].data

    if image is None:
        raise Exception("Missing input data")

    data_g = np.fft.fft2(image)
    out = np.fft.fftshift(np.abs(data_g) ** 2)

    outputs = {
        "diffractogram": RawPort(meta=inputs["image"].meta, data=out),
    }

    return outputs
