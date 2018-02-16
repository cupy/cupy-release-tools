ARG base_image
FROM ${base_image}

RUN yum -y update && \
    yum clean all

# Install Python libraries.
ARG cython_version
RUN for PYTHON_HOME in /opt/python/*/; do \
      echo "Installing libraries on Python under ${PYTHON_HOME}..." && \
      ${PYTHON_HOME}/bin/pip install -U pip setuptools && \
      ${PYTHON_HOME}/bin/pip install argparse && \
      ${PYTHON_HOME}/bin/pip install Cython==${cython_version} wheel auditwheel; \
    done

# Use Python 3.6 by default to run the agent.
COPY agent.py /
ENTRYPOINT ["/opt/python/cp36-cp36m/bin/python", "/agent.py"]
