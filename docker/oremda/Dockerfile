FROM python:3.9-slim-bullseye

RUN apt-get update && \
  apt-get install -y \
    git \
    gcc && \
  rm -rf /var/lib/apt/lists/*

# Just copy over the parts that we need. Eventually we should probably split the
# repo.
COPY  setup.py pyproject.toml /oremda/
COPY  oremda /oremda/oremda/
COPY  ./.git /oremda/.git/

RUN pip install -e /oremda && \
  rm -rf /oremda/.git


# Ensure messages get flushed immediately for debugging.
# This is especially important in containers, where the messages
# may not be printed at all if the buffer did not get flushed.
ENV PYTHONUNBUFFERED=1
