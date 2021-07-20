ARG BASE_IMAGE=centos:7
FROM ${BASE_IMAGE}

RUN yum -y install "@Core" "@Development Tools"

ARG CUDA_INSTALLER_URL
RUN curl -sL -o /tmp/cuda_installer "${CUDA_INSTALLER_URL}" && \
    bash /tmp/cuda_installer --silent --toolkit && \
    ls -al /usr/local/cuda && \
    rm /tmp/cuda_installer

ENV CUDA_PATH /usr/local/cuda
ENV PATH /usr/local/nvidia/bin:/usr/local/cuda/bin:${PATH}
ENV LD_LIBRARY_PATH /usr/local/nvidia/lib:/usr/local/nvidia/lib64:/usr/local/cuda/lib64
ENV LIBRARY_PATH /usr/local/cuda/lib64/stubs

# NVIDIA Container Toolkit (nvidia-docker)
ENV NVIDIA_VISIBLE_DEVICES all
