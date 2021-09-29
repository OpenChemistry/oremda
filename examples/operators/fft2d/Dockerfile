ARG BASE_IMAGE=oremda/oremda

FROM ${BASE_IMAGE}

COPY run.py /

LABEL oremda.name="fft2d" \
      oremda.ports.input.in.type="data" \
      oremda.ports.output.real.type="data" \
      oremda.ports.output.imag.type="data"

ENTRYPOINT ["python", "/run.py"]
