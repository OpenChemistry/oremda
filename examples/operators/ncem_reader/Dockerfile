FROM oremda/oremda

RUN pip install \
  ncempy

COPY run.py /

LABEL oremda.name="ncem_reader" \
      oremda.ports.output.eloss.type="data" \
      oremda.ports.output.spec.type="data" \
      oremda.params.filename.type="string" \
      oremda.params.filename.required="true"

ENTRYPOINT ["python", "/run.py"]
