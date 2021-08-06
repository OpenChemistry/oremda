#!/usr/bin/env python3

from oremda.clients.utils import nested_to_flat


if __name__ == "__main__":

    import json
    import sys

    if len(sys.argv) < 2:
        sys.exit("usage: <script> <json_file>")

    with open(sys.argv[1], "r") as rf:
        d = json.load(rf)

    labels = nested_to_flat(d)

    ending = "\\\n  "
    output = "LABEL "
    for key, value in labels.items():
        output += f"{key}={value} {ending}"

    output = output[: -len(ending)]
    print(output)
