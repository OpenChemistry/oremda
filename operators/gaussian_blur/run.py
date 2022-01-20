from typing import Dict

from scipy.ndimage import gaussian_filter

from oremda.api import operator
from oremda.typing import JSONType, PortKey, RawPort


@operator
def gaussian_blur(
    inputs: Dict[PortKey, RawPort], parameters: JSONType
) -> Dict[PortKey, RawPort]:

    sigma = parameters.get("sigma", 0)
    image = inputs["image"].data

    if image is not None:
        image = gaussian_filter(image, sigma=sigma)

    outputs = {"image": RawPort(meta=inputs["image"].meta, data=image)}

    return outputs
