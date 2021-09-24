ARG BASE_IMAGE=oremda/peak_base

FROM ${BASE_IMAGE}

COPY run.py /

LABEL oremda.name="peak_opt" \
      oremda.ports.input.image.type="data" \
      oremda.ports.input.peaks.type="data" \
      oremda.ports.output.peaks.type="data"\
      oremda.ports.output.sigmas.type="data"\
      oremda.params.cutout.type="number"

ENTRYPOINT ["python", "/run.py"]
