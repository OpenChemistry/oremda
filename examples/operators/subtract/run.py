from typing import Dict, Tuple

import numpy as np

from oremda import operator
from oremda.typing import JSONType, PortKey, MetaType, DataType


def eloss_to_pixel(eloss, energy):
    aa = np.where(eloss >= energy)[0]
    return aa[0]


@operator
def subtract(
    meta: Dict[PortKey, MetaType], data: Dict[PortKey, DataType], parameters: JSONType
) -> Tuple[Dict[PortKey, MetaType], Dict[PortKey, DataType]]:
    start = parameters.get("start", 0)
    stop = parameters.get("stop", 0)

    eloss = data["eloss"]
    spec = data["spec"]
    eloss_bg = data["eloss_bg"]
    background = data["background"]

    start_spec = eloss_to_pixel(eloss, start)
    stop_spec = eloss_to_pixel(eloss, stop)
    start_bg = eloss_to_pixel(eloss_bg, start)
    stop_bg = eloss_to_pixel(eloss_bg, stop)

    assert stop_spec - start_spec == stop_bg - start_bg

    output_data = {
        "eloss": eloss[start_spec:stop_spec],
        "spec": spec[start_spec:stop_spec] - background[start_bg:stop_bg],
    }

    return {}, output_data
