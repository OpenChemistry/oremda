ARG BASE_IMAGE=oremda/oremda

FROM ${BASE_IMAGE}

RUN pip install \
  Pillow

COPY run.py /

LABEL oremda.name="tiff_reader" \
      oremda.ports.input.data.type="binary" \
      oremda.ports.output.out.type="image" \
      oremda.params.filename.type="string"

USER oremda

ENTRYPOINT ["python", "/run.py"]
