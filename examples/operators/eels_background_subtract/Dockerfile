FROM oremda/oremda

RUN pip install \
  matplotlib \
  numpy \
  ncempy

COPY run.py /

ENTRYPOINT ["python", "/run.py"]
