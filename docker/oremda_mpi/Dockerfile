FROM oremda/oremda

RUN apt-get update && \
  apt-get install -y \
    libmpich-dev && \
  rm -rf /var/lib/apt/lists/*

RUN pip install mpi4py
