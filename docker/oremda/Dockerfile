FROM python:3.9

COPY . /oremda

RUN pip install -e /oremda

RUN useradd -u 1001 oremda

# Ensure messages get flushed immediately for debugging.
# This is especially important in containers, where the messages
# may not be printed at all if the buffer did not get flushed.
ENV PYTHONUNBUFFERED=1
