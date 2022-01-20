from typing import Dict

from oremda.api import operator
from oremda.typing import JSONType, PortKey, RawPort


@operator(name="print")
def print_(
    inputs: Dict[PortKey, RawPort], parameters: JSONType
) -> Dict[PortKey, RawPort]:
    print(f"{inputs=}, {parameters=}")
    return {}
