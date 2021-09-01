from typing import Dict

from oremda import operator
from oremda.typing import JSONType, PortKey, RawPort, DisplayType


@operator
def picture(
    inputs: Dict[PortKey, RawPort], parameters: JSONType
) -> Dict[PortKey, RawPort]:
    scalars = inputs["in"].data

    outputs = {"out": RawPort(meta={"type": DisplayType.TwoD}, data=scalars)}

    return outputs
