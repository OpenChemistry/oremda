from typing import Dict

from oremda.api import operator
from oremda.typing import JSONType, PortKey, RawPort

import peakFind  # type: ignore


@operator
def peak_opt(
    inputs: Dict[PortKey, RawPort], parameters: JSONType
) -> Dict[PortKey, RawPort]:

    cutout = parameters.get("cutout", 6)
    image = inputs["image"].data
    peaks = inputs["peaks"].data

    if image is None or peaks is None:
        raise Exception('Data is missing from the "in" port')

    opt_peaks, optI, fitting_values = peakFind.fit_peaks_gauss2d(
        image, peaks, cutout, (2.5, 2.5), ((-1.5, -1.5, 0, 0), (1.5, 1.5, 8, 8))
    )

    outputs = {
        "peaks": RawPort(data=opt_peaks[:, 0:2]),
        "sigmas": RawPort(data=opt_peaks[:, 2:4]),
    }

    return outputs
