from typing import Dict

from oremda.api import operator
from oremda.typing import JSONType, PortKey, RawPort

DATA_FILE_NAME = "/data.tiff"


@operator
def data_container(
    _inputs: Dict[PortKey, RawPort], parameters: JSONType
) -> Dict[PortKey, RawPort]:

    with open(DATA_FILE_NAME, "br") as f:
        data = f.read()

    outputs = {
        "data": RawPort(data=data),
    }

    return outputs
