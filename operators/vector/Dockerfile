ARG BASE_IMAGE=oremda/oremda

FROM ${BASE_IMAGE}

COPY run.py /

LABEL oremda.name="vector" \
      oremda.ports.input.origin.type="data" \
      oremda.ports.input.direction.type="data" \
      oremda.ports.output.out.type="display" \
      oremda.params.z.type="number" \
      oremda.params.color.type="string" \
      oremda.params.label.type="string"

USER oremda

ENTRYPOINT ["python", "/run.py"]
