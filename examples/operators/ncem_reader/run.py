from typing import Dict

from pathlib import Path

import ncempy.io as nio

from oremda import operator
from oremda.typing import JSONType, PortKey, RawPort


@operator
def ncem_reader(_inputs: Dict[PortKey, RawPort], parameters: JSONType) -> Dict[PortKey, RawPort]:
    filename = parameters.get("filename", "")

    dPath = Path("/data")
    fPath = Path(filename)

    spectrum = nio.read(dPath / fPath)
    eloss = spectrum["coords"][1]
    spec = spectrum["data"][0, :]

    outputs = {
        "eloss": RawPort(data=eloss),
        "spec": RawPort(data=spec),
    }

    return outputs
