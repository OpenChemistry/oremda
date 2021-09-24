from typing import Dict

from oremda import operator
from oremda.typing import (
    JSONType,
    PortKey,
    RawPort,
    DisplayType,
    PlotType2D,
)


@operator
def picture(
    inputs: Dict[PortKey, RawPort], parameters: JSONType
) -> Dict[PortKey, RawPort]:
    z = parameters.get("z", 0)
    normalize = parameters.get("normalize")

    scalars = inputs["in"].data

    outputs = {
        "out": RawPort(
            meta={
                "type": DisplayType.TwoD,
                "plot": PlotType2D.Image,
                "z": z,
                "normalize": normalize,
            },
            data=scalars,
        )
    }

    return outputs
