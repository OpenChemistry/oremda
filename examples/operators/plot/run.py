from typing import Dict

import numpy as np

from oremda import operator
from oremda.typing import JSONType, PortKey, RawPort, DisplayType


@operator
def plot(inputs: Dict[PortKey, RawPort], parameters: JSONType) -> Dict[PortKey, RawPort]:
    label = parameters["label"]
    x = inputs["x"].data
    y = inputs["y"].data

    outputs = {
        'out': RawPort(
            meta={
                "type": DisplayType.OneD,
                "label": label
            },
            data=np.array([x, y])
        )
    }

    return outputs
