from typing import Dict

from oremda import operator
from oremda.typing import JSONType, PortKey, RawPort


@operator
def crop2d(
    inputs: Dict[PortKey, RawPort], parameters: JSONType
) -> Dict[PortKey, RawPort]:

    image = inputs["image"].data
    bounds = parameters.get("bounds")

    if image is None:
        raise Exception("Missing input data")

    if bounds is None:
        slice_x = slice(None, None, None)
        slice_y = slice(None, None, None)
    else:
        slice_x = slice(bounds[0], bounds[1], None)
        slice_y = slice(bounds[2], bounds[3], None)

    outputs = {
        "image": RawPort(meta=inputs["image"].meta, data=image[slice_y, slice_x]),
    }

    return outputs
