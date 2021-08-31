from typing import Dict

import numpy as np

from oremda import operator
from oremda.typing import JSONType, PortKey, RawPort


def eloss_to_pixel(eloss, energy):
    aa = np.where(eloss >= energy)[0]
    return aa[0]


@operator
def subtract(
    inputs: Dict[PortKey, RawPort], parameters: JSONType
) -> Dict[PortKey, RawPort]:
    start = parameters.get("start", 0)
    stop = parameters.get("stop", 0)

    eloss = inputs["eloss"].data
    spec = inputs["spec"].data
    eloss_bg = inputs["eloss_bg"].data
    background = inputs["background"].data

    assert eloss is not None
    assert spec is not None
    assert eloss_bg is not None
    assert background is not None

    start_spec = eloss_to_pixel(eloss, start)
    stop_spec = eloss_to_pixel(eloss, stop)
    start_bg = eloss_to_pixel(eloss_bg, start)
    stop_bg = eloss_to_pixel(eloss_bg, stop)

    assert stop_spec - start_spec == stop_bg - start_bg

    outputs = {
        "eloss": RawPort(data=eloss[start_spec:stop_spec]),
        "spec": RawPort(data=spec[start_spec:stop_spec] - background[start_bg:stop_bg]),
    }

    return outputs
