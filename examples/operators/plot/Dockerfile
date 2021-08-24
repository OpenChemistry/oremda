ARG BASE_IMAGE=oremda/oremda

FROM ${BASE_IMAGE}

RUN pip install \
  matplotlib

COPY run.py /

LABEL oremda.name="plot" \
      oremda.ports.input.x0.type="data" \
      oremda.ports.input.y0.type="data" \
      oremda.ports.input.x1.type="data" \
      oremda.ports.input.y1.type="data" \
      oremda.ports.input.x1.required="false" \
      oremda.ports.input.y1.required="false" \
      oremda.params.filename.type="string" \
      oremda.params.filename.required="true" \
      oremda.params.xLabel.type="string" \
      oremda.params.xLabel.required="true" \
      oremda.params.yLabel.type="string" \
      oremda.params.yLabel.required="true"

ENTRYPOINT ["python", "/run.py"]
