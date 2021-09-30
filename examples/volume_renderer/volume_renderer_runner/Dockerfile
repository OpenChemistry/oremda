FROM oremda/oremda

RUN pip install \
  six

COPY run.py /
COPY pipeline.json /

USER oremda

ENTRYPOINT ["python", "/run.py"]
