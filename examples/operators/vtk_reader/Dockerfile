ARG BASE_IMAGE=oremda/oremda

FROM ${BASE_IMAGE}

# libgl1-mesa-glx is required for VTK
RUN apt-get update && \
    apt-get install -y \
      libgl1-mesa-glx && \
    rm -rf /var/lib/apt/lists/*

RUN pip install vtk

COPY run.py /

LABEL oremda.name="vtk_reader" \
      oremda.ports.output.data.type="data" \
      oremda.params.filename.type="string" \
      oremda.params.filename.required="true"

USER oremda

ENTRYPOINT ["python", "/run.py"]
