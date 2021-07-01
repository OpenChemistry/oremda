import numpy as np

from oremda import operator

def eloss_to_pixel(eloss, energy):
    aa = np.where(eloss >= energy)[0]
    return aa[0]

@operator
def subtract(meta, data, parameters):
    start = parameters.get('start', 0)
    stop = parameters.get('stop', 0)

    eloss = data.get('eloss')
    spec = data.get('spec')
    eloss_bg = data.get('eloss_bg')
    background = data.get('background')

    start_spec = eloss_to_pixel(eloss, start)
    stop_spec = eloss_to_pixel(eloss, stop)
    start_bg = eloss_to_pixel(eloss_bg, start)
    stop_bg = eloss_to_pixel(eloss_bg, stop)

    assert(stop_spec - start_spec == stop_bg - start_bg)

    output_data = {
        'eloss': eloss[start_spec:stop_spec],
        'spec': spec[start_spec:stop_spec] - background[start_bg:stop_bg],
    }

    return {}, output_data
