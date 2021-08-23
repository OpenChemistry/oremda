FROM oremda/oremda

RUN pip install \
  six

COPY run.py /
COPY pipeline.json /

ENTRYPOINT ["python", "/run.py"]
