from pathlib import Path

import ncempy.io as nio

from oremda import operator

@operator
def ncem_reader(meta, data, parameters):
    filename = parameters.get('filename')

    dPath = Path('/data')
    fPath = Path(filename)

    spectrum = nio.read(dPath / fPath)
    eloss = spectrum['coords'][1]
    spec = spectrum['data'][0,:]

    output_meta = {}

    output_data = {
        'eloss': eloss,
        'spec': spec,
    }

    return output_meta, output_data
