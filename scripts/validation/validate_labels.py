#!/usr/bin/env python

import sys

from oremda.clients import client_from_image


if len(sys.argv) < 2:
    sys.exit('Usage: <script> <image>')

image_path = sys.argv[1]
client = client_from_image(image_path)

image = client.image(image_path)
image.validate_labels()
print('Labels are valid!')
