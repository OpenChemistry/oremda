from typing import Dict

from oremda import operator
from oremda.typing import JSONType, PortKey, RawPort


@operator(_name="print")
def print_(
    inputs: Dict[PortKey, RawPort], parameters: JSONType
) -> Dict[PortKey, RawPort]:
    print(f"{inputs=}, {parameters=}")
    return inputs
