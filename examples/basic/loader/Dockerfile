FROM oremda/oremda

RUN pip install pyarrow

COPY run.py /

# Since we leave this image open until the end, make sure all
# output gets printed as it comes in.
ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["python", "/run.py"]
