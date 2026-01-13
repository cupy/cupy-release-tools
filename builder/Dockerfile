ARG base_image
FROM ${base_image}

COPY setup_yum_centos7.sh /

# Run twice for EPEL.
RUN /setup_yum_centos7.sh && \
    yum -y install gcc gcc-c++ make patch git curl && \
    yum -y install bzip2-devel openssl-devel readline-devel libffi-devel && \
    yum -y install epel-release && \
    yum-config-manager --disable epel && \
    /setup_yum_centos7.sh && \
    yum -y install --enablerepo=epel openssl11-devel && \
    yum clean all

# Install Python.
ARG python_versions
RUN git clone https://github.com/pyenv/pyenv.git /opt/pyenv
ENV PYENV_ROOT=/opt/pyenv
ENV PATH=${PYENV_ROOT}/shims:${PYENV_ROOT}/bin:${PATH}
COPY requirements.cupy-build.txt /
COPY setup_python.sh /
RUN /setup_python.sh "${python_versions}"

# Install devtoolset (g++) for CuPy v8 build.
RUN yum install -y centos-release-scl && \
    /setup_yum_centos7.sh && \
    yum install -y devtoolset-7-gcc-c++ && \
    yum clean all

# Install additional libraries for CUDA.
COPY cuda_lib/ /cuda_lib
COPY setup_cuda_opt_lib.py /
RUN /setup_cuda_opt_lib.py --src /cuda_lib --dst /usr/local/cuda

# Install additional dependicies.
ARG system_packages
RUN [ -z "${system_packages}" ] || ( \
        yum -y install ${system_packages} && \
        yum clean all \
    )

# Add build agent.
COPY build-wrapper /
COPY agent.py /

ENTRYPOINT ["/agent.py"]
