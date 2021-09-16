from typing import Dict, Optional

from oremda.display import DisplayHandle
from oremda.typing import DisplayType, IdType, Port

import matplotlib.pyplot as plt


class MatplotlibDisplayHandle1D(DisplayHandle):
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


class MatplotlibDisplayHandle2D(DisplayHandle):
    def __init__(self, id: IdType):
        super().__init__(id, DisplayType.TwoD)
        self.sourceId: Optional[IdType] = None
        self.input: Optional[Port] = None

    def add(self, sourceId: IdType, input: Port):
        self.sourceId = sourceId
        self.input = input
        self.render()

    def remove(self, sourceId: IdType):
        if self.sourceId == sourceId:
            self.sourceId = None
            self.input = None

        self.render()

    def clear(self):
        self.sourceId = None
        self.input = None
        self.render()

    def render(self):
        if self.input is None:
            return

        array = self.input.data

        if array is None:
            return

        data = array.data

        cmap = plt.cm.get_cmap("viridis", 16)
        norm = plt.Normalize(vmin=data.min(), vmax=data.max())

        plt.imsave(f"/data/{self.id}.png", cmap(norm(data)))
