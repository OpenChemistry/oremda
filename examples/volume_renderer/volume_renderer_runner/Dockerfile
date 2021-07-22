FROM oremda/oremda

RUN pip install \
  six

COPY run.py /
COPY pipeline.json /

# Since we leave this image open until the end, make sure all
# output gets printed as it comes in.
ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["python", "/run.py"]
