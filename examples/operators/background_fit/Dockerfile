ARG BASE_IMAGE=oremda/oremda

FROM ${BASE_IMAGE}

RUN pip install \
  numpy

COPY run.py /

LABEL oremda.name="background_fit" \
      oremda.ports.input.eloss.type="data" \
      oremda.ports.input.spec.type="data" \
      oremda.ports.output.eloss.type="data" \
      oremda.ports.output.background.type="data" \
      oremda.params.start.type="number" \
      oremda.params.start.required="true" \
      oremda.params.stop.type="number" \
      oremda.params.stop.required="true"

USER oremda

ENTRYPOINT ["python", "/run.py"]
