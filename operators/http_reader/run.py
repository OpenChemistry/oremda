from typing import Dict
from io import BytesIO
from pathlib import Path

from oremda import operator
from oremda.typing import JSONType, PortKey, RawPort

import requests


CACHE_FILE_NAME = "data.binary"


def download_file(url, filename=None):
    buffer = BytesIO()
    with requests.get(url, stream=True) as r:
        r.raise_for_status()

        f = None
        if filename is not None:
            f = open(filename, "wb")

        try:
            for chunk in r.iter_content(chunk_size=8192):
                buffer.write(chunk)
                if f is not None:
                    f.write(chunk)
        finally:
            if f is not None:
                f.close()

    return buffer.getvalue()


@operator
def http_reader(
    _inputs: Dict[PortKey, RawPort], parameters: JSONType
) -> Dict[PortKey, RawPort]:

    url = parameters.get("url")
    if url is None:
        raise Exception("A 'url' parameter must be configured.")
    cache = parameters.get("cache", True)

    # First check the cache if enabled
    print(Path(CACHE_FILE_NAME).exists())
    if cache and Path(CACHE_FILE_NAME).exists():
        with open(CACHE_FILE_NAME, "br") as f:
            data = f.read()
    # Download the file
    else:
        filename = None
        if cache:
            filename = CACHE_FILE_NAME

        data = download_file(url, filename=filename)

    outputs = {
        "data": RawPort(data=data),
    }

    return outputs
