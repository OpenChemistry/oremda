ARG BASE_IMAGE=oremda/oremda

FROM ${BASE_IMAGE}

RUN pip install scipy

COPY run.py /

LABEL oremda.name="gaussian_blur" \
      oremda.ports.input.in.type="data" \
      oremda.ports.output.out.type="data"

ENTRYPOINT ["python", "/run.py"]
