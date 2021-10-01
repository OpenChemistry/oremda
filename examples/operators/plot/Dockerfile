ARG BASE_IMAGE=oremda/oremda

FROM ${BASE_IMAGE}

COPY run.py /

LABEL oremda.name="plot" \
      oremda.ports.input.x.type="data" \
      oremda.ports.input.y.type="data" \
      oremda.ports.output.out.type="display"

USER oremda

ENTRYPOINT ["python", "/run.py"]
