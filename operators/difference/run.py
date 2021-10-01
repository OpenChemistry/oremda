from typing import Dict

from oremda import operator
from oremda.typing import JSONType, PortKey, RawPort


@operator
def difference(
    inputs: Dict[PortKey, RawPort], parameters: JSONType
) -> Dict[PortKey, RawPort]:
    a = inputs["a"].data
    b = inputs["b"].data

    if a is None or b is None:
        raise Exception('Data is missing from the "in" port')

    if a.shape != b.shape:
        raise Exception("Incompatible shape.", a.shape, b.shape, a[0], b[0])

    diff = a - b

    outputs = {
        "diff": RawPort(data=diff),
    }

    return outputs
