ARG BASE_IMAGE=oremda/peak_base

FROM ${BASE_IMAGE}

COPY run.py /

LABEL oremda.name="lattice_find" \
      oremda.ports.input.image.type="data" \
      oremda.ports.input.peaks.type="data" \
      oremda.ports.output.origin.type="data" \
      oremda.ports.output.u.type="data" \
      oremda.ports.output.v.type="data" \
      oremda.ports.output.lattice.type="data"

USER oremda

ENTRYPOINT ["python", "/run.py"]
