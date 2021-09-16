ARG BASE_IMAGE=oremda/oremda

FROM ${BASE_IMAGE}

COPY run.py /

LABEL oremda.name="picture" \
      oremda.ports.input.in.type="data" \
      oremda.ports.output.out.type="display"

ENTRYPOINT ["python", "/run.py"]
