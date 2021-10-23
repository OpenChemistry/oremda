ARG BASE_IMAGE=oremda/oremda

FROM ${BASE_IMAGE}

# Installing the latest py4DSTEM (0.12.6) can be painful, because we
# because we are using python 3.9, and py4DSTEM used to fix their
# dependency versions, many of which do not have python 3.9 wheels,
# and building them all is difficult. As such, let's just install
# py4DSTEM from it's dev git repository so we don't have to build
# all of the dependencies... I hope the next version of py4DSTEM
# doesn't have the dependencies fixed.

# Install python dependencies
RUN pip install \
  ncempy \
  git+https://github.com/py4DSTEM/py4DSTEM.git@7e4933ecd593e36702a4b7a34ee13c67d2ffea9d

RUN mkdir -p /bvm/
COPY run.py /bvm/

LABEL oremda.name="bragg_vector_map" \
      oremda.ports.output.out.type="data" \
      oremda.params.filename.type="string" \
      oremda.params.filename.required="true" \
      oremda.mpi.parallel_aware="true"

USER oremda

ENTRYPOINT ["python", "/bvm/run.py"]
