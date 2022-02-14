from typing import Dict

import numpy as np

from oremda.api import operator
from oremda.typing import JSONType, PortKey, RawPort


def power_fit(sig, box):
    """Fit a power law to the EELS background.

    Parameters
    ----------
    sig : ndarray
        Spectra as a 1D array with shape (energy_loss, ).

    box : tuple
        The starting and ending point (in pixels) for the
        powerLaw background subtraction.

    Returns
    -------
    : tuple
        A tuple of the background values and the energy loss values (in pixels).

    Example
    -------
        >> bgnd, bgnd_eloss = power_fit(spectrum, (100, 120))

    """
    eLoss = np.linspace(box[0], box[1] - 1, int(np.abs(box[1] - box[0])))
    try:
        yy = np.copy(sig)
        yy[yy < 0] = 0
        yy += 1

        pp = np.polyfit(np.log(eLoss), np.log(yy[box[0] : box[1]]), 1)  # log-log fit
    except Exception:
        print("fitting problem")
        pp = (0, 0)
        raise
    # fullEloss = np.linspace(0, sig.shape[0], sig.shape[0], endpoint=False)
    fullEloss = np.linspace(box[0], sig.shape[0], int(np.abs(sig.shape[0] - box[0])))
    try:
        bgnd = np.exp(pp[1]) * fullEloss ** pp[0]
    except Exception:
        print("bgnd creation problem")
        bgnd = np.zeros_like(fullEloss)
    return bgnd, fullEloss


def eloss_to_pixel(eloss, energy):
    aa = np.where(eloss >= energy)[0]
    return aa[0]


@operator
def background_fit(
    inputs: Dict[PortKey, RawPort], parameters: JSONType
) -> Dict[PortKey, RawPort]:
    start_eloss = parameters.get("start", 0)
    stop_eloss = parameters.get("stop", 0)

    eloss = inputs["eloss"].data
    spec = inputs["spec"].data

    assert eloss is not None
    assert spec is not None

    start = eloss_to_pixel(eloss, start_eloss)
    end = eloss_to_pixel(eloss, stop_eloss)

    background, _ = power_fit(spec, (start, end))

    outputs: Dict[PortKey, RawPort] = {
        "eloss": RawPort(data=eloss[start:]),
        "background": RawPort(data=background),
    }

    return outputs
