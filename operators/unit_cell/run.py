from typing import Dict

import numpy as np
from scipy import ndimage

from oremda.api import operator
from oremda.typing import JSONType, PortKey, RawPort

import peakFind  # type: ignore


@operator
def unit_cell(
    inputs: Dict[PortKey, RawPort], parameters: JSONType
) -> Dict[PortKey, RawPort]:
    image = inputs["image"].data
    origin = inputs["origin"].data
    u = inputs["u"].data
    v = inputs["v"].data
    oversample = parameters.get("oversample", 1)

    if image is None or origin is None or u is None or v is None:
        raise Exception('Data is missing from the "in" port')

    num_u = int(np.sqrt(np.dot(u, u)) * oversample)
    num_v = int(num_u * (np.linalg.norm(v) / np.linalg.norm(u)))
    uu = [ii / num_u for ii in u]
    vv = [ii / num_v for ii in v]

    unit_cell = np.zeros((num_v, num_u), dtype=np.float32)
    cur_cell = np.zeros((num_v * num_u,), dtype=np.float32)

    QQ = peakFind.lattice2D(u, v, 1, 1, origin, (10, 10))
    WW = peakFind.lattice2D(
        uu, vv, 1, 1, (0, 0), (num_u, num_v)
    )  # starts at (0,0). Then add each peak.

    for ii, peak in enumerate(QQ):
        cur_XX = WW[:, 0] + peak[0]
        cur_YY = WW[:, 1] + peak[1]
        ndimage.map_coordinates(
            image.astype(np.float32),
            (cur_XX.ravel(), cur_YY.ravel()),
            order=3,
            output=cur_cell,
            cval=np.NAN,
        )
        if not np.any(np.isnan(cur_cell)):
            unit_cell += cur_cell.reshape((num_v, num_u))

    # Normalize by the number of unit cells used
    unit_cell /= QQ.shape[0]

    # Rotate to match the image
    unit_cell = unit_cell.T

    outputs = {
        "image": RawPort(data=unit_cell),
    }

    return outputs
