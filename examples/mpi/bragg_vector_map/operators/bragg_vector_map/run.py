from pathlib import Path
from typing import Dict

import ncempy.io as nio

import py4DSTEM
from py4DSTEM.io.datastructure import PointListArray
from py4DSTEM.process.diskdetection.braggvectormap import (
    get_bragg_vector_map_raw,
)
from py4DSTEM.process.diskdetection.diskdetection import (
    find_Bragg_disks_selected,
)
from py4DSTEM.process.diskdetection.probe import (
    get_probe_from_vacuum_2Dimage,
    get_probe_kernel_edge_gaussian,
)

from oremda.api import operator
from oremda.typing import JSONType, PortKey, RawPort
from oremda.utils.concurrency import distribute_tasks


def generate_bragg_vector_map(datacube, probe, R_xys, **kwargs):
    r_shape = (datacube.R_Nx, datacube.R_Ny)
    q_shape = (datacube.Q_Nx, datacube.Q_Ny)

    coords = [("qx", float), ("qy", float), ("intensity", float)]
    peaks = PointListArray(coordinates=coords, shape=r_shape)

    # Generate the peaks for the requested Rxs and Rys
    Rxs, Rys = list(zip(*R_xys))
    ret_peaks = find_Bragg_disks_selected(datacube, probe, Rxs, Rys, **kwargs)

    # Set the peaks on our PointListArray
    for i, (Rx, Ry) in enumerate(R_xys):
        peaks.pointlists[Rx][Ry] = ret_peaks[i]

    # Sum what we found together
    return get_bragg_vector_map_raw(peaks, *q_shape)


def load_dm3_file(filepath):
    datacube = py4DSTEM.io.read(filepath, mem="MEMMAP")

    # The DM3 file is old and DM3 can't store 4D data...only 3D data
    # We wrote tags in the DM3 with the correct shape.
    # Get the correct shape and set it
    # FIXME: hard coded
    with nio.dm.fileDM(filepath) as dm1:
        dm1.parseHeader()
        scanI = int(dm1.allTags[".ImageList.2.ImageTags.Series.nimagesx"])
        scanJ = int(dm1.allTags[".ImageList.2.ImageTags.Series.nimagesy"])

    datacube.set_scan_shape(scanJ, scanI)  # set the shape. DM3 can't store 4D
    return datacube


def generate_probe_kernel(datacube):
    # FIXME: hard coded
    # Top line has no sample to diffract
    dp0 = datacube.data[0, 0:10, :, :].sum(axis=0)
    probe = get_probe_from_vacuum_2Dimage(dp0)
    return get_probe_kernel_edge_gaussian(probe, sigma_probe_scale=2)


@operator
def bragg_vector_map(
    inputs: Dict[PortKey, RawPort], parameters: JSONType
) -> Dict[PortKey, RawPort]:
    filename = parameters.get("filename", "")
    parallel_index = parameters.get("parallel_index")
    parallel_world_size = parameters.get("parallel_world_size")

    data_path = Path("/data")
    datacube = load_dm3_file(data_path / filename)
    probe = generate_probe_kernel(datacube)

    # FIXME: hard coded
    kwargs = {
        "corrPower": 1,
        "sigma": 1,
        "edgeBoundary": 20,
        "minRelativeIntensity": 0.0005,
        "relativeToPeak": 0,
        "minPeakSpacing": 10,
        "maxNumPeaks": 180,
        "subpixel": "multicorr",
        "upsample_factor": 4,
    }

    # Generate R_xys for the indices requested
    r_shape = (datacube.R_Nx, datacube.R_Ny)
    R_xys = [(i, j) for i in range(r_shape[0]) for j in range(r_shape[1])]

    if parallel_index is not None and parallel_world_size is not None:
        tasks = distribute_tasks(len(R_xys), parallel_world_size)
        local_task = tasks[parallel_index]
        R_xys = [R_xys[i] for i in range(*local_task)]

    output = generate_bragg_vector_map(datacube, probe, R_xys, **kwargs)

    outputs = {
        "out": RawPort(data=output),
    }

    return outputs
