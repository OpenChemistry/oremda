ARG BASE_IMAGE=oremda/oremda

FROM ${BASE_IMAGE}

RUN pip install scipy

COPY run.py /

LABEL oremda.name="gaussian_blur" \
      oremda.ports.input.image.type="data" \
      oremda.ports.output.image.type="data"

USER oremda

ENTRYPOINT ["python", "/run.py"]
