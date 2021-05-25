FROM python:3.8

RUN pip install pyarrow

COPY run.sh /

ENTRYPOINT ["bash", "/run.sh"]
