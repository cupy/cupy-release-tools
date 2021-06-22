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
