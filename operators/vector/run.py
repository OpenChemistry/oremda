from typing import Dict

import numpy as np
from oremda.api import operator
from oremda.typing import JSONType, PortKey, RawPort, DisplayType, PlotType2D


@operator
def vector(
    inputs: Dict[PortKey, RawPort], parameters: JSONType
) -> Dict[PortKey, RawPort]:
    z = parameters.get("z", 0)
    color = parameters.get("color")
    label = parameters.get("label")

    origin = inputs["origin"].data
    direction = inputs["direction"].data

    v = np.concatenate((origin, direction))
    vectors = v.reshape((1, len(v)))

    outputs = {
        "out": RawPort(
            meta={
                "type": DisplayType.TwoD,
                "plot": PlotType2D.Vectors,
                "z": z,
                "color": color,
                "label": label,
            },
            data=vectors,
        )
    }

    return outputs
