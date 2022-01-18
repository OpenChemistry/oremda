ARG BASE_IMAGE=oremda/oremda

FROM ${BASE_IMAGE}

COPY run.py /

LABEL oremda.name="picture" \
      oremda.ports.input.in.type="image" \
      oremda.ports.output.out.type="display" \
      oremda.params.z.type="number" \
      oremda.params.normalize.type="string"

USER oremda

ENTRYPOINT ["python", "/run.py"]
