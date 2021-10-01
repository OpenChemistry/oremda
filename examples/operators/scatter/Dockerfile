ARG BASE_IMAGE=oremda/oremda

FROM ${BASE_IMAGE}

COPY run.py /

LABEL oremda.name="scatter" \
      oremda.ports.input.in.type="data" \
      oremda.ports.output.out.type="display" \
      oremda.params.z.type="number" \
      oremda.params.marker_style.type="string" \
      oremda.params.marker_size.type="number"

USER oremda

ENTRYPOINT ["python", "/run.py"]
