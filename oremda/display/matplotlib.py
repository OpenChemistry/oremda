from typing import Dict

from oremda.display import DisplayHandle
from oremda.typing import DisplayType, IdType, Port

import matplotlib.pyplot as plt


class MatplotlibDisplayHandle(DisplayHandle):
    def __init__(self, id: IdType):
        super().__init__(id, DisplayType.OneD)
        self.inputs: Dict[IdType, Port] = {}

    def add(self, sourceId: IdType, input: Port):
        self.inputs[sourceId] = input
        self.render()

    def remove(self, sourceId: IdType):
        if id in self.inputs:
            del self.inputs[sourceId]
        self.render()

    def clear(self):
        self.inputs = {}
        self.render()

    def render(self):
        x_label = self.parameters.get("xLabel", "x")
        y_label = self.parameters.get("yLabel", "y")

        fg, ax = plt.subplots(1, 1)

        for port in self.inputs.values():
            if port.data is None:
                continue

            x = port.data.data[0]
            y = port.data.data[1]

            label = None
            if port.meta is not None:
                label = port.meta.get("label")

            ax.plot(x, y, label=label)

        ax.legend()
        ax.set(xlabel=x_label, ylabel=y_label)

        fg.savefig(f"/data/{self.id}.png", dpi=fg.dpi)
