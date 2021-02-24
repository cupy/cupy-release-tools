ARG base_image
FROM ${base_image}

RUN sed -ie 's|#baseurl=http://mirror.centos.org/centos/|baseurl=http://ftp.iij.ad.jp/pub/linux/centos-vault/centos/|g' /etc/yum.repos.d/CentOS-Base.repo
RUN yum -y install gcc gcc-c++ make patch git curl && \
    yum -y install bzip2-devel openssl-devel readline-devel libffi-devel && \
    yum clean all

# Install pyenv.
RUN git clone https://github.com/pyenv/pyenv.git /opt/pyenv
ENV PYENV_ROOT=/opt/pyenv
ENV PATH ${PYENV_ROOT}/shims:${PYENV_ROOT}/bin:${PATH}

# Install Python.
ARG python_versions
ARG cython_version
COPY setup_python.sh /
RUN /setup_python.sh "${python_versions}" "${cython_version}"

# Install devtoolset (g++) for CuPy v8 build.
COPY setup_devtoolset.sh /
RUN /setup_devtoolset.sh

# Install NCCL.
COPY nccl /nccl
RUN ( [ ! -d /nccl/lib ]     || mv /nccl/lib/*     /usr/local/cuda/lib64 ) && \
    ( [ ! -d /nccl/include ] || mv /nccl/include/* /usr/local/cuda/include ) && \
    ldconfig

# Install cuDNN.
COPY cudnn /cudnn
RUN ( [ ! -d /cudnn/cuda/lib64 ]   || mv /cudnn/cuda/lib64/*   /usr/local/cuda/lib64 ) && \
    ( [ ! -d /cudnn/cuda/include ] || mv /cudnn/cuda/include/* /usr/local/cuda/include ) && \
    ldconfig

# Install additional dependencies for ROCm.
RUN [ ! -d /opt/rocm ] || ( \
        yum -y install hipcub4.0.1 hipblas4.0.1 rocrand4.0.1 rocfft4.0.1 rocsolver4.0.1 rccl4.0.1 && \
        yum clean all \
    )

# Install requirements for agents.
RUN yum -y install python-setuptools && \
    yum clean all
RUN easy_install argparse

# Add build agent.
COPY build-wrapper /
COPY agent.py /

ENTRYPOINT ["/agent.py"]
