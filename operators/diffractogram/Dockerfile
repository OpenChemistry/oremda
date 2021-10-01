ARG BASE_IMAGE=oremda/oremda

FROM ${BASE_IMAGE}

COPY run.py /

LABEL oremda.name="diffractogram" \
      oremda.ports.input.image.type="data" \
      oremda.ports.output.diffractogram.type="data"

USER oremda

ENTRYPOINT ["python", "/run.py"]
