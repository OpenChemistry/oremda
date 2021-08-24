from typing import Dict

import matplotlib.pyplot as plt

from oremda import operator
from oremda.typing import JSONType, PortKey, RawPort


@operator
def plot(inputs: Dict[PortKey, RawPort], parameters: JSONType) -> Dict[PortKey, RawPort]:
    filename = parameters.get("filename")
    x_label = parameters.get("xLabel", "x")
    y_label = parameters.get("yLabel", "y")

    empty_port = RawPort()
    x0 = inputs.get("x0", empty_port).data
    y0 = inputs.get("y0", empty_port).data
    x1 = inputs.get("x1", empty_port).data
    y1 = inputs.get("y1", empty_port).data

    fg, ax = plt.subplots(1, 1)

    if x0 is not None and y0 is not None:
        ax.plot(x0, y0)

    if x1 is not None and y1 is not None:
        ax.plot(x1, y1)

    ax.set(xlabel=x_label, ylabel=y_label)

    fg.savefig(f"/data/{filename}", dpi=fg.dpi)

    return {}
