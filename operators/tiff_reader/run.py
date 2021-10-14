from typing import Dict
from pathlib import Path
from PIL import Image
import numpy as np
from io import BytesIO

from oremda import operator
from oremda.typing import JSONType, PortKey, RawPort


@operator
def tiff_reader(
    _inputs: Dict[PortKey, RawPort], parameters: JSONType
) -> Dict[PortKey, RawPort]:

    # First check for a data port
    if "data" in _inputs:
        img = Image.open(BytesIO(_inputs["data"].data))
    else:
        filename = parameters.get("filename")
        if filename is None:
            raise Exception("Data port or filename must be provided.")

        dPath = Path("/data")
        fPath = Path(filename)

        img = Image.open(str(dPath / fPath))

    scalars = np.array(img)

    outputs = {
        "out": RawPort(data=scalars),
    }

    return outputs
