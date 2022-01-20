import os
from pathlib import Path
import subprocess

from typing import Dict

import numpy as np

import vtk

from vtk.util.numpy_support import numpy_to_vtk  # type: ignore

from oremda.api import operator
from oremda.typing import JSONType, PortKey, RawPort

ren_win = vtk.vtkRenderWindow()
ren_win.OffScreenRenderingOn()

ren = vtk.vtkRenderer()
ren_win.AddRenderer(ren)

iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(ren_win)
style = vtk.vtkInteractorStyleTrackballCamera()
iren.SetInteractorStyle(style)

ren_win.SetSize(800, 600)
ren_win.SetWindowName("Volumes")


def activate_virtual_framebuffer():
    """
    Activates a virtual (headless) framebuffer for rendering 3D
    scenes via VTK.

    Most critically, this function is useful when this code is being run
    in a Dockerized notebook, or over a server without X forwarding.

    * Requires the following packages:
      * `sudo apt-get install libgl1-mesa-dev xvfb`
    """

    os.environ["DISPLAY"] = ":99.0"

    commands = ["Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &", "sleep 3"]

    for command in commands:
        subprocess.call(command, shell=True)


# This is necessary for any kind of rendering in the container
activate_virtual_framebuffer()


def array_to_image_data(arr):
    if arr.ndim == 2:
        arr = arr[..., np.newaxis]

    image_data = vtk.vtkImageData()
    image_data.SetDimensions(*arr.shape)

    pd = image_data.GetPointData()
    pd.SetScalars(numpy_to_vtk(arr.ravel()))

    return image_data


def create_color_function(arr, points=None, data_range=None):
    if points is None:
        points = [
            (0, 0, 0),
            (1, 0, 0),
            (0, 1, 0),
            (0, 0, 1),
        ]

    if data_range is not None:
        amin, amax = data_range
    else:
        amin, amax = np.nanmin(arr), np.nanmax(arr)

    steps = np.linspace(amin, amax, len(points))

    color_function = vtk.vtkColorTransferFunction()
    for step, point in zip(steps, points):
        color_function.AddRGBPoint(step, *point)

    return color_function


def create_opacity_function(arr, values=None, data_range=None):
    if values is None:
        values = [
            0.0,
            0.1,
            0.7,
            1.0,
        ]

    if data_range is not None:
        amin, amax = data_range
    else:
        amin, amax = np.nanmin(arr), np.nanmax(arr)

    steps = np.linspace(amin, amax, len(values))

    opacity_function = vtk.vtkPiecewiseFunction()
    for step, value in zip(steps, values):
        opacity_function.AddPoint(step, value)

    return opacity_function


def add_volume(arr):
    image_data = array_to_image_data(arr)

    producer = vtk.vtkTrivialProducer()
    producer.SetOutput(image_data)

    color = create_color_function(arr)
    opacity = create_opacity_function(arr)

    volume = vtk.vtkVolume()
    mapper = vtk.vtkGPUVolumeRayCastMapper()
    prop = vtk.vtkVolumeProperty()

    prop.SetColor(color)
    prop.SetScalarOpacity(opacity)
    mapper.SetInputConnection(producer.GetOutputPort())
    mapper.SetMaskTypeToBinary()

    volume.SetMapper(mapper)
    volume.SetProperty(prop)

    ren.AddViewProp(volume)


def write_window(ren_win, filename):
    w2i_filter = vtk.vtkWindowToImageFilter()
    writer = vtk.vtkPNGWriter()

    w2i_filter.SetInput(ren_win)
    writer.SetInputConnection(w2i_filter.GetOutputPort())
    writer.SetFileName(str(filename))
    writer.Write()


@operator
def stateful_volume_renderer(
    inputs: Dict[PortKey, RawPort], parameters: JSONType
) -> Dict[PortKey, RawPort]:
    filename = parameters.get("filename", "")
    clear = parameters.get("clear", False)

    filepath = Path("/data") / filename

    if clear:
        ren.RemoveAllViewProps()

    add_volume(inputs["data"].data)

    ren.ResetCamera()
    ren_win.Render()

    write_window(ren_win, filepath)

    return {}
