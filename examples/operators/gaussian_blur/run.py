from typing import Dict

import numpy as np
from scipy.ndimage import gaussian_filter

from oremda import operator
from oremda.typing import JSONType, PortKey, RawPort, DisplayType


@operator
def gaussian_blur(
    inputs: Dict[PortKey, RawPort], parameters: JSONType
) -> Dict[PortKey, RawPort]:

    sigma = parameters.get("sigma", 0)
    data = inputs["in"].data

    if data is not None:
        data = gaussian_filter(data, sigma=sigma)

    outputs = {"out": RawPort(meta=inputs["in"].meta, data=data)}

    return outputs
