ARG BASE_IMAGE=oremda/oremda

FROM ${BASE_IMAGE}

RUN pip install \
  requests

COPY run.py /

LABEL oremda.name="http_reader" \
      oremda.ports.output.data.type="binary" \
      oremda.params.url.type="string" \
      oremda.params.url.required="true" \
      oremda.params.cache.type="bool" \
      oremda.params.cache.required="false"

USER oremda

ENTRYPOINT ["python", "/run.py"]
