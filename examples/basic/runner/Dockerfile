ARG BASE_IMAGE=oremda/oremda

FROM ${BASE_IMAGE}

RUN pip install matplotlib

### SINGULARITY SECTION ###
RUN apt-get update && \
    apt-get install -y \
      build-essential \
      libssl-dev \
      uuid-dev \
      libgpgme11-dev \
      squashfs-tools \
      libseccomp-dev \
      pkg-config && \
    rm -rf /var/lib/apt/lists/*

RUN export VERSION=1.17 OS=linux ARCH=amd64 && \
    wget https://dl.google.com/go/go$VERSION.$OS-$ARCH.tar.gz && \
    tar -C /usr/local -xzvf go$VERSION.$OS-$ARCH.tar.gz && \
    rm go$VERSION.$OS-$ARCH.tar.gz && \
    echo 'export GOPATH=${PWD}/go' >> /setup_go_env.sh && \
    echo 'export PATH=/usr/local/go/bin:${PATH}:${GOPATH}/bin' >> /setup_go_env.sh

RUN . /setup_go_env.sh && \
    export VERSION=3.8.1 && \
    mkdir -p $GOPATH/src/github.com/hpcng && \
    cd $GOPATH/src/github.com/hpcng && \
    wget https://github.com/hpcng/singularity/releases/download/v${VERSION}/singularity-${VERSION}.tar.gz && \
    tar -xzf singularity-${VERSION}.tar.gz && \
    cd ./singularity-${VERSION} && \
    ./mconfig && \
    make -C ./builddir && \
    make -C ./builddir install

RUN mkdir /runner
COPY run.py pipeline.json /runner/

ENTRYPOINT ["python", "/runner/run.py"]
