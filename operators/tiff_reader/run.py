from typing import Dict
from pathlib import Path
from PIL import Image
import numpy as np

from oremda import operator
from oremda.typing import JSONType, PortKey, RawPort


@operator
def tiff_reader(
    _inputs: Dict[PortKey, RawPort], parameters: JSONType
) -> Dict[PortKey, RawPort]:
    filename = parameters.get("filename", "")

    dPath = Path("/data")
    fPath = Path(filename)

    img = Image.open(str(dPath / fPath))

    scalars = np.array(img)

    outputs = {
        "out": RawPort(data=scalars),
    }

    return outputs
