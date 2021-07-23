FROM oremda/oremda

# libgl1-mesa-glx is required for VTK
# xvfb is required to make a virtual frame buffer for rendering
RUN apt-get update && \
    apt-get install -y \
      libgl1-mesa-glx \
      xvfb && \
    rm -rf /var/lib/apt/lists/*

RUN pip install vtk

COPY run.py /

LABEL oremda.name="stateful_volume_renderer" \
      oremda.ports.input.data.type="data" \
      oremda.params.filename.type="string" \
      oremda.params.filename.required="true" \
      oremda.params.clear.type="bool" \
      oremda.params.clear.required="false"

ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["python", "/run.py"]
