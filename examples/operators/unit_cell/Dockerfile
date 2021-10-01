ARG BASE_IMAGE=oremda/peak_base

FROM ${BASE_IMAGE}

COPY run.py /

LABEL oremda.name="unit_cell" \
      oremda.ports.input.image.type="data" \
      oremda.ports.input.origin.type="data" \
      oremda.ports.input.u.type="data" \
      oremda.ports.input.v.type="data" \
      oremda.ports.output.image.type="data" \
      oremda.params.oversample.type="number"

USER oremda

ENTRYPOINT ["python", "/run.py"]
