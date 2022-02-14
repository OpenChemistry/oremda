from typing import Dict

from oremda.api import operator
from oremda.typing import JSONType, PortKey, RawPort, DisplayType, PlotType1D


@operator
def histograms(
    inputs: Dict[PortKey, RawPort], parameters: JSONType
) -> Dict[PortKey, RawPort]:
    z = parameters.get("z", 0)
    color = parameters.get("color")
    label = parameters.get("label")
    bins = parameters.get("bins")

    data = inputs["in"].data

    if data is None:
        raise Exception("Missing input data.")

    outputs = {
        "out": RawPort(
            meta={
                "type": DisplayType.OneD,
                "plot": PlotType1D.Histograms,
                "z": z,
                "bins": bins,
                "color": color,
                "label": label,
            },
            data=data.ravel(),
        )
    }

    return outputs
