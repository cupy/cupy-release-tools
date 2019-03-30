ARG base_image
FROM ${base_image}

RUN yum -y update && \
    yum -y install gcc gcc-c++ make patch git curl && \
    yum -y install bzip2-devel openssl-devel readline-devel libffi-devel && \
    yum clean all

# Install OpenSSL; Python 3.7 requires OpenSSL 1.0.2 or 1.1 compatible libssl
# with X509_VERIFY_PARAM_set1_host, whereas CentOS 6 provides 0.9.8 and 1.0.1.
ENV OPENSSL_ROOT=openssl-1.0.2o
ENV OPENSSL_FILE=${OPENSSL_ROOT}.tar.gz
ENV OPENSSL_HASH=ec3f5c9714ba0fd45cb4e087301eb1336c317e0d20b575a125050470e8089e4d
RUN curl -s -q -o "${OPENSSL_FILE}" "https://www.openssl.org/source/${OPENSSL_FILE}" && \
    echo "${OPENSSL_HASH}  ${OPENSSL_FILE}" | sha256sum -cw --quiet - && \
    tar xf "${OPENSSL_FILE}" && \
    cd "${OPENSSL_ROOT}" && \
    ./config no-ssl2 no-shared -fPIC --prefix=/usr/local/ssl &> /tmp/openssl-config.log && \
    make &> /tmp/openssl-make.log && \
    make install_sw &> /tmp/openssl-make-install_sw.log && \
    cd .. && \
    rm -rf "${OPENSSL_ROOT}" "${OPENSSL_ROOT}.tar.gz"
ENV CFLAGS=-I/usr/local/ssl/include
ENV LDFLAGS=-L/usr/local/ssl/lib

# Install pyenv.
RUN git clone https://github.com/pyenv/pyenv.git /opt/pyenv
ENV PYENV_ROOT=/opt/pyenv
ENV PATH ${PYENV_ROOT}/shims:${PYENV_ROOT}/bin:${PATH}

# Install Python.
ARG python_versions
RUN for VERSION in ${python_versions}; do \
      echo "Installing Python ${VERSION}..." && \
      pyenv install ${VERSION}; \
    done;

# Install Python libraries.
ARG cython_version
RUN for VERSION in ${python_versions}; do \
      echo "Installing libraries on Python ${VERSION}..." && \
      pyenv global ${VERSION} && \
      pip install -U pip setuptools && \
      pip install argparse && \
      pip install Cython==${cython_version} wheel auditwheel; \
    done && \
    pyenv global system

# Install requirements for agents.
RUN yum -y install python-setuptools && yum clean all
RUN easy_install argparse

# Install NCCL
COPY nccl /nccl
RUN ( [ ! -d /nccl/lib ]     || mv /nccl/lib/*     /usr/local/cuda/lib64 ) && \
    ( [ ! -d /nccl/include ] || mv /nccl/include/* /usr/local/cuda/include ) && \
    ldconfig

COPY agent.py /
ENTRYPOINT ["/agent.py"]
