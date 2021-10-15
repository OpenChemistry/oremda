ARG BASE_IMAGE=oremda/oremda

FROM ${BASE_IMAGE}

RUN pip install scipy

COPY run.py /

LABEL oremda.name="gaussian_blur" \
      oremda.description="Apply a Gaussian filter" \
      oremda.ports.input.image.type="image" \
      oremda.ports.output.image.type="image"

USER oremda

ENTRYPOINT ["python", "/run.py"]
