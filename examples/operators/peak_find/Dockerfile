ARG BASE_IMAGE=oremda/peak_base

FROM ${BASE_IMAGE}

COPY run.py /

LABEL oremda.name="peak_find" \
      oremda.ports.input.image.type="data" \
      oremda.ports.output.peaks.type="data"\
      oremda.params.threshold.type="number" \
      oremda.params.min_distance.type="number"

ENTRYPOINT ["python", "/run.py"]
