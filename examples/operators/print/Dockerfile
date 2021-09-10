ARG BASE_IMAGE=oremda/oremda

FROM ${BASE_IMAGE}

RUN pip install \
  numpy

COPY run.py /

LABEL oremda.name="print" \
      oremda.ports.input.data.type="data" \
      oremda.ports.output.data.type="data"

ENTRYPOINT ["python", "/run.py"]
