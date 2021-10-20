from typing import Dict

from pathlib import Path

import ncempy.io as nio

from oremda import operator
from oremda.typing import JSONType, PortKey, RawPort, EELSMetadata, Metadata


@operator
def ncem_reader_eels(
    _inputs: Dict[PortKey, RawPort], parameters: JSONType
) -> Dict[PortKey, RawPort]:
    filename = parameters.get("filename", "")

    dPath = Path("/data")
    fPath = Path(filename)

    spectrum = nio.read(dPath / fPath)
    eloss = spectrum["coords"][1]
    spec = spectrum["data"][0, :]

    meta = Metadata(dataset=EELSMetadata(units=spectrum["pixelUnit"]))

    outputs = {
        "eloss": RawPort(data=eloss, meta=meta),
        "spec": RawPort(data=spec, meta=meta),
    }

    return outputs
