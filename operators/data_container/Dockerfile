ARG BASE_IMAGE=oremda/oremda

FROM ${BASE_IMAGE}

COPY run.py /
COPY data.tiff /

LABEL oremda.name="data_container" \
      oremda.ports.output.data.type="binary"

USER oremda

ENTRYPOINT ["python", "/run.py"]
