from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import ncempy.io as nio

from oremda import operator


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
    eLoss = np.linspace(box[0], box[1]-1, int(np.abs(box[1] - box[0])))
    try:
        yy = sig
        yy[yy < 0] = 0
        yy += 1

        pp = np.polyfit(np.log(eLoss), np.log(yy[box[0]:box[1]]), 1) #log-log fit
    except:
        print('fitting problem')
        pp = (0,0)
        raise
    fullEloss = np.linspace(box[0], sig.shape[0], np.int(np.abs(sig.shape[0] - box[0])))
    try:
        bgnd = np.exp(pp[1])*fullEloss**pp[0]
    except:
        print('bgnd creation problem')
        bgnd = np.zeros_like(fullEloss)
    return bgnd, fullEloss


def eloss_to_pixel(eloss, energy):
    aa = np.where(eloss >= energy)[0]
    return aa[0]


@operator
def eels_background_subtract(data, params):
    dPath = Path('/data')
    fPath = Path('08_carbon.dm3')

    start_eloss = params.get('start', 0)
    stop_eloss = params.get('stop', 0)

    spectrum = nio.read(dPath / fPath)
    eloss = spectrum['coords'][1]
    spec = spectrum['data'][0,:]

    fg, ax = plt.subplots(1, 1)
    ax.scatter(eloss, spec)
    ax.set(xlabel='eLoss (eV)')
    ax2 = ax.twiny()
    ax2.plot(spec)
    ax2.set(xlabel='pixel')

    fg.savefig('input.png', dpi=fg.dpi)

    start = eloss_to_pixel(eloss, start_eloss)
    end = eloss_to_pixel(eloss, stop_eloss)

    bgnd, eloss2 = power_fit(spec, (start, end))

    fg, ax = plt.subplots(1, 2)
    ax[0].plot(eloss2, bgnd, label='background')
    ax[0].plot(spec, label='raw')
    ax[1].plot(spec[start:] - bgnd, label='background subtracted')
    ax[0].legend()
    ax[1].legend()
    fg.tight_layout()

    fg.savefig('output.png', dpi=fg.dpi)
