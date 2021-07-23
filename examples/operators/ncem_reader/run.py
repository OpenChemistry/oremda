from typing import Dict, Tuple

from pathlib import Path

import ncempy.io as nio

from oremda import operator
from oremda.typing import JSONType, PortKey, MetaType, DataType

@operator
def ncem_reader(
        meta: Dict[PortKey, MetaType],
        data: Dict[PortKey, DataType],
        parameters: JSONType
    ) -> Tuple[Dict[PortKey, MetaType], Dict[PortKey, DataType]]:
    filename = parameters.get('filename', '')

    dPath = Path('/data')
    fPath = Path(filename)

    spectrum = nio.read(dPath / fPath)
    eloss = spectrum['coords'][1]
    spec = spectrum['data'][0,:]

    output_meta: Dict[PortKey, MetaType] = {}

    output_data: Dict[PortKey, DataType] = {
        'eloss': eloss,
        'spec': spec,
    }

    return output_meta, output_data
