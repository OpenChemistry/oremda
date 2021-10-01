ARG BASE_IMAGE=oremda/oremda

FROM ${BASE_IMAGE}

RUN pip install \
  Pillow

COPY run.py /

LABEL oremda.name="tiff_reader" \
      oremda.ports.output.out.type="data" \
      oremda.params.filename.type="string" \
      oremda.params.filename.required="true"

USER oremda

ENTRYPOINT ["python", "/run.py"]
