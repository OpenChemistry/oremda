from abc import abstractmethod
import os
from typing import Any, Dict, cast
import matplotlib
import numpy as np

from oremda.display import DisplayHandle
from oremda.typing import (
    DisplayType,
    IdType,
    NormalizeType,
    PlotType1D,
    PlotType2D,
    Port,
)
from oremda.constants import DEFAULT_DATA_DIR

import matplotlib.pyplot as plt
import matplotlib.colors


class BaseMatplotLibDisplayHandle(DisplayHandle):
    def __init__(self, id: IdType, type: DisplayType):
        super().__init__(id, type)
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
        data_dir = os.environ.get("OREMDA_DATA_DIR") or DEFAULT_DATA_DIR
        filename = os.path.join(data_dir, f"{self.id}.png")
        file_obj = open(filename, "wb")
        self.raw_render(file_obj)
        file_obj.close()

    @abstractmethod
    def raw_render(self, file_obj):
        pass


class MatplotlibDisplayHandle1D(BaseMatplotLibDisplayHandle):
    def __init__(self, id: IdType):
        super().__init__(id, DisplayType.OneD)

    def raw_render(self, file_obj):
        inputs = sorted(self.inputs.values(), key=z_sort)

        x_label = self.parameters.get("xLabel", "x")
        y_label = self.parameters.get("yLabel", "y")

        legend = False
        fig, ax = plt.subplots()

        for port in inputs:
            data = port.data
            meta = port.meta or {}
            if data is None:
                continue

            plot = meta.get("plot", PlotType1D.Line)
            label = meta.get("label")
            color = meta.get("color")

            if plot is None:
                continue

            legend = legend or label is not None

            if plot == PlotType1D.Line:
                x = data.data[0]
                y = data.data[1]
                ax.plot(x, y, label=label, color=color)
            elif plot == PlotType1D.Scatter:
                marker = meta.get("marker", ".")
                x = data.data[0]
                y = data.data[1]
                ax.plot(x, y, label=label, marker=marker, color=color, linestyle="None")
            elif plot == PlotType1D.Histograms:
                bins = meta.get("bins", 10)
                ax.hist(data.data, bins=bins, label=label, color=color)

        if legend:
            ax.legend()

        ax.set(xlabel=x_label, ylabel=y_label)

        fig.savefig(file_obj, dpi=fig.dpi)
        plt.close()


class MatplotlibDisplayHandle2D(BaseMatplotLibDisplayHandle):
    def __init__(self, id: IdType):
        super().__init__(id, DisplayType.TwoD)

    def raw_render(self, file_obj):
        inputs = sorted(self.inputs.values(), key=z_sort)

        fig, ax = plt.subplots()

        legend = False

        for input in inputs:
            array = input.data

            if array is None:
                continue

            data = cast(np.ndarray, array.data)
            meta = input.meta or {}
            plot = meta.get("plot")
            label = meta.get("label")

            if plot is None:
                continue

            legend = legend or label is not None

            if plot == PlotType2D.Image:
                norm = None
                normalize = meta.get("normalize")
                if normalize == NormalizeType.Linear:
                    norm = matplotlib.colors.Normalize(vmin=data.min(), vmax=data.max())
                elif normalize == NormalizeType.Log:
                    norm = matplotlib.colors.LogNorm(vmin=data.min(), vmax=data.max())

                ax.imshow(data, norm=norm)

            elif plot == PlotType2D.Points:
                color = meta.get("color", "red")
                marker: Any = meta.get("marker", ".")
                size = meta.get("size")
                ax.scatter(
                    data[:, 0], data[:, 1], s=size, c=color, marker=marker, label=label
                )

            elif plot == PlotType2D.Vectors:
                color = meta.get("color", "red")
                for vector in data:
                    ax.arrow(
                        vector[1],
                        vector[0],
                        vector[3],
                        vector[2],
                        color=color,
                        label=label,
                    )

        if legend:
            ax.legend()

        fig.savefig(file_obj, dpi=fig.dpi)
        plt.close()


def z_sort(port: Port):
    meta = port.meta or {}
    z = meta.get("z", 0)
    return z
