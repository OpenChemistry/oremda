from typing import Dict

import numpy as np

from oremda import operator
from oremda.typing import JSONType, PortKey, RawPort

import peakFind  # type: ignore


@operator
def lattice_find(
    inputs: Dict[PortKey, RawPort], parameters: JSONType
) -> Dict[PortKey, RawPort]:
    image = inputs["image"].data
    peaks = inputs["peaks"].data

    if image is None or peaks is None:
        raise Exception('Data is missing from the "in" port')

    p0 = peaks

    # Find the center atom
    cMid = image.shape[0] / 2
    modelRR = np.sqrt(
        np.sum((p0 - cMid) ** 2, axis=1)
    )  # Distances from middle of particle
    centerAtom = modelRR.argmin()  # Minimum distance from NP middle

    # Input starting guess at vectors
    origin0 = p0[centerAtom, :].copy()
    pA = (289, 290)  # point A; input as (y, x) from matplotlib plot
    pB = (288, 215)  # point B; input as (y, x) from matplotlb plot
    fraction = (1, 1)  # used if unit cell contains atoms not at the corners
    num_unit_cells = (
        4,
        4,
    )  # used if u0 and v0 are loner than 1 unit cell (more accurate)

    # Calculte the initial u0 and v0
    u0 = [pA[0] - origin0[0], pA[1] - origin0[1]]
    v0 = [pB[0] - origin0[0], pB[1] - origin0[1]]

    origin, u, v, ab = peakFind.refineLattice2D(
        origin0,
        u0,
        v0,
        p0,
        refine_locally=True,
        fraction=fraction,
        num_unit_cells=num_unit_cells,
    )

    uv = np.asarray((u, v))
    ab_nearest = np.dot(p0 - origin, np.linalg.inv(uv))
    lattice = np.dot(np.round(ab_nearest), uv) + origin

    outputs = {
        "origin": RawPort(data=origin),
        "u": RawPort(data=u),
        "v": RawPort(data=v),
        "lattice": RawPort(data=lattice),
    }

    return outputs
