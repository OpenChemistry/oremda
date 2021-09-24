ARG BASE_IMAGE=oremda/oremda

FROM ${BASE_IMAGE}

COPY run.py /

LABEL oremda.name="difference" \
      oremda.ports.input.a.type="data" \
      oremda.ports.input.b.type="data" \
      oremda.ports.output.diff.type="data"

ENTRYPOINT ["python", "/run.py"]
