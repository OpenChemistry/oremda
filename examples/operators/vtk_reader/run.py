from pathlib import Path

import numpy as np

import vtk
from vtk.numpy_interface import dataset_adapter as dsa

from oremda import operator


READERS = {
    "vtk": vtk.vtkStructuredPointsReader,
    "vti": vtk.vtkXMLImageDataReader,
}


def read_file(file_name):
    ext = Path(file_name).suffix[1:]
    if ext not in READERS:
        raise Exception(f"Unknown extension: {ext}")

    reader = READERS[ext]()
    reader.SetFileName(str(file_name))
    reader.Update()
    return reader.GetOutput()


def to_numpy_array(data_object, key=None):
    wrapped = dsa.WrapDataObject(data_object)
    pd = wrapped.PointData

    if key is None:
        # Grab the first key we can find
        key = next(iter(pd.keys()))

    vtk_array = pd[key].reshape(data_object.GetDimensions())
    return np.array(vtk_array)


@operator
def vtk_reader(meta, data, parameters):
    filename = parameters.get("filename", "")
    filepath = Path("/data") / filename

    data = read_file(filepath)

    output = {"data": to_numpy_array(data)}

    return meta, output
