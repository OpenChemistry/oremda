ARG BASE_IMAGE=oremda/oremda

FROM ${BASE_IMAGE}

COPY run.py /

LABEL oremda.name="histograms" \
      oremda.ports.input.in.type="data" \
      oremda.ports.output.out.type="display" \
      oremda.params.z.type="number" \
      oremda.params.bins.type="number" \
      oremda.params.label.type="string" \
      oremda.params.color.type="string"

USER oremda

ENTRYPOINT ["python", "/run.py"]
