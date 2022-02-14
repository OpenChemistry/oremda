from typing import Dict, Any

from oremda.api import operator
from oremda.typing import JSONType, PortKey, RawPort

import peakFind  # type: ignore


@operator
def peak_find(
    inputs: Dict[PortKey, RawPort], parameters: JSONType
) -> Dict[PortKey, RawPort]:

    threshold = parameters.get("threshold", 0.5)
    min_distance = parameters.get("min_distance", 5)
    data = inputs["image"].data

    if data is None:
        raise Exception('Data is missing from the "image" port')

    coords_found: Any = peakFind.peakFind2D(data, threshold)
    coords_found = peakFind.enforceMinDist(
        coords_found, data[coords_found[:, 0], coords_found[:, 1]], min_distance
    )

    outputs = {"peaks": RawPort(data=coords_found)}

    return outputs
