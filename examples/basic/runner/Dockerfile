ARG BASE_IMAGE=oremda/oremda

FROM ${BASE_IMAGE}

RUN mkdir /runner
COPY run.py pipeline.json /runner/

ENTRYPOINT ["python", "/runner/run.py"]
