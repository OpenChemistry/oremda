from typing import Dict

import numpy as np

from oremda import operator
from oremda.typing import JSONType, PortKey, RawPort


@operator
def tile(
    inputs: Dict[PortKey, RawPort], parameters: JSONType
) -> Dict[PortKey, RawPort]:
    image = inputs["image"].data
    n_x = parameters.get("n_x", 1)
    n_y = parameters.get("n_y", 1)

    if image is None:
        raise Exception('Data is missing from the "in" port')

    outputs = {"image": RawPort(data=np.tile(image, (n_y, n_x)))}

    return outputs
