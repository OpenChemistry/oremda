ARG BASE_IMAGE=oremda/oremda

FROM ${BASE_IMAGE}

RUN pip install scipy

USER oremda

COPY peakFind.py gaussND.py /
