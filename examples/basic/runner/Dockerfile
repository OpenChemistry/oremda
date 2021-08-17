ARG BASE_IMAGE=oremda/oremda

FROM ${BASE_IMAGE}

COPY run.py /
COPY pipeline.json /

ENTRYPOINT ["python", "/run.py"]
