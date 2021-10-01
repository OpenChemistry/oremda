ARG BASE_IMAGE=oremda/oremda

FROM ${BASE_IMAGE}

RUN pip install \
  ncempy

COPY run.py /

LABEL oremda.name="ncem_reader_eels" \
      oremda.ports.output.eloss.type="data" \
      oremda.ports.output.spec.type="data" \
      oremda.params.filename.type="string" \
      oremda.params.filename.required="true"

USER oremda

ENTRYPOINT ["python", "/run.py"]
