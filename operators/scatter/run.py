from typing import Dict

from oremda.api import operator
from oremda.typing import JSONType, PortKey, RawPort, DisplayType, PlotType2D


@operator
def scatter(
    inputs: Dict[PortKey, RawPort], parameters: JSONType
) -> Dict[PortKey, RawPort]:
    z = parameters.get("z", 0)
    color = parameters.get("color")
    marker = parameters.get("marker")
    size = parameters.get("size")
    label = parameters.get("label")

    points = inputs["in"].data

    outputs = {
        "out": RawPort(
            meta={
                "type": DisplayType.TwoD,
                "plot": PlotType2D.Points,
                "z": z,
                "color": color,
                "marker": marker,
                "size": size,
                "label": label,
            },
            data=points,
        )
    }

    return outputs
