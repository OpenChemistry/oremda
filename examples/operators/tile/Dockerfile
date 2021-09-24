ARG BASE_IMAGE=oremda/oremda

FROM ${BASE_IMAGE}

COPY run.py /

LABEL oremda.name="tile" \
      oremda.ports.input.image.type="data" \
      oremda.ports.output.image.type="data" \
      oremda.params.n_x.type="number" \
      oremda.params.n_y.type="number"

ENTRYPOINT ["python", "/run.py"]
