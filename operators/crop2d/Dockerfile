ARG BASE_IMAGE=oremda/oremda

FROM ${BASE_IMAGE}

COPY run.py /

LABEL oremda.name="crop2d" \
      oremda.ports.input.image.type="data" \
      oremda.ports.output.image.type="data"

USER oremda

ENTRYPOINT ["python", "/run.py"]
