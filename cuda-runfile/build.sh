#!/bin/bash

set -uex

# https://developer.nvidia.com/cuda-11.0-download-archive?target_os=Linux&target_arch=x86_64&target_distro=CentOS&target_version=7&target_type=runfilelocal
docker build -t cupy/cupy-release-tools:cuda-runfile-11.0.2-centos7 . \
    --build-arg CUDA_INSTALLER_URL="https://developer.download.nvidia.com/compute/cuda/11.0.2/local_installers/cuda_11.0.2_450.51.05_linux.run" &

# https://developer.nvidia.com/cuda-11.1.0-download-archive?target_os=Linux&target_arch=x86_64&target_distro=CentOS&target_version=7&target_type=runfilelocal
docker build -t cupy/cupy-release-tools:cuda-runfile-11.1.0-centos7 . \
    --build-arg CUDA_INSTALLER_URL="https://developer.download.nvidia.com/compute/cuda/11.1.0/local_installers/cuda_11.1.0_455.23.05_linux.run" &

# https://developer.nvidia.com/cuda-11.2.0-download-archive?target_os=Linux&target_arch=x86_64&target_distro=CentOS&target_version=7&target_type=runfilelocal
docker build -t cupy/cupy-release-tools:cuda-runfile-11.2.0-centos7 . \
    --build-arg CUDA_INSTALLER_URL="https://developer.download.nvidia.com/compute/cuda/11.2.0/local_installers/cuda_11.2.0_460.27.04_linux.run" &

# https://developer.nvidia.com/cuda-11.3.0-download-archive?target_os=Linux&target_arch=x86_64&target_distro=CentOS&target_version=7&target_type=runfile_local
docker build -t cupy/cupy-release-tools:cuda-runfile-11.3.0-centos7 . \
    --build-arg CUDA_INSTALLER_URL="https://developer.download.nvidia.com/compute/cuda/11.3.0/local_installers/cuda_11.3.0_465.19.01_linux.run" &

wait
