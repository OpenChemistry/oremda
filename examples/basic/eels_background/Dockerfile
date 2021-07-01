FROM oremda/oremda

RUN pip install pyarrow

COPY run_json.py /
COPY pipeline.json /

# Since we leave this image open until the end, make sure all
# output gets printed as it comes in.
ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["python", "/run_json.py"]
