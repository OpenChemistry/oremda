FROM python:3.9-slim-bullseye

RUN apt-get update && \
  apt-get install -y \
    curl gcc && \
  rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -

COPY  /core /oremda/core
COPY  /api /oremda/api

# TODO: We should have option to install from PyPI for now just build and install
# oremda-api and its dep oremda-core.
RUN . $HOME/.poetry/env && \
  cd /oremda/core && \
  poetry build && \
  pip install dist/*.whl

RUN . $HOME/.poetry/env && \
  cd /oremda/api && \
  poetry build && \
  pip install dist/*.whl

RUN useradd -u 1001 oremda

# Ensure messages get flushed immediately for debugging.
# This is especially important in containers, where the messages
# may not be printed at all if the buffer did not get flushed.
ENV PYTHONUNBUFFERED=1
