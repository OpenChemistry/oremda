#!/usr/bin/env python3

"""docker_to_singularity.py

This script will create a singularity image from a docker image,
and transfer the docker labels over to the singularity image.

This script will no longer be needed if this issue is resolved:
https://github.com/sylabs/singularity/issues/146
"""

import os
import re
import tempfile
import sys

import docker
from spython.main import Client as sclient

if len(sys.argv) < 2:
    sys.exit("Usage: <script> <docker_image>")

dclient = docker.from_env()
image_name = sys.argv[1]

image = dclient.images.get(image_name)
labels = image.labels

labels_string = ""
for key, value in labels.items():
    labels_string += f"    {key} {value}\n"

definition = f"""\
Bootstrap: docker-daemon
From: {image.id}

%labels
{labels_string}
"""

output_name = re.sub("[:/]", "_", f"{image_name}.sif")

tf = tempfile.NamedTemporaryFile("w", delete=False)
try:
    tf.close()
    with open(tf.name, "w") as wf:
        wf.write(definition)

    sclient.build(tf.name, image=output_name)
finally:
    os.unlink(tf.name)
    del tf
