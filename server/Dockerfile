FROM oremda/oremda

RUN pip install \
    fastapi \
    uvicorn[standard]

COPY server /server

# Since we leave this image open until the end, make sure all
# output gets printed as it comes in.
ENV PYTHONUNBUFFERED=1

EXPOSE 80

ENTRYPOINT ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "80"]
