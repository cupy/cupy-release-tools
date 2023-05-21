#!/bin/bash

set -uex

CUDA="$1"
IMAGE_SUFFIX="centos7"
BASE_IMAGE="centos:7"

case ${CUDA} in
  10.2 )
    CUDA_VERSION="10.2.89"
    CUDA_INSTALLER_URL="https://developer.download.nvidia.com/compute/cuda/10.2/Prod/local_installers/cuda_10.2.89_440.33.01_linux.run"
    ;;
  11.0 )
    CUDA_VERSION="11.0.2"
    CUDA_INSTALLER_URL="https://developer.download.nvidia.com/compute/cuda/11.0.2/local_installers/cuda_11.0.2_450.51.05_linux.run"
    ;;
  11.1 )
    CUDA_VERSION="11.1.0"
    CUDA_INSTALLER_URL="https://developer.download.nvidia.com/compute/cuda/11.1.0/local_installers/cuda_11.1.0_455.23.05_linux.run"
    ;;
  11.2 )
    CUDA_VERSION="11.2.0"
    CUDA_INSTALLER_URL="https://developer.download.nvidia.com/compute/cuda/11.2.0/local_installers/cuda_11.2.0_460.27.04_linux.run"
    ;;
  11.3 )
    CUDA_VERSION="11.3.0"
    CUDA_INSTALLER_URL="https://developer.download.nvidia.com/compute/cuda/11.3.0/local_installers/cuda_11.3.0_465.19.01_linux.run"
    ;;
  11.4 )
    CUDA_VERSION="11.4.0"
    CUDA_INSTALLER_URL="https://developer.download.nvidia.com/compute/cuda/11.4.0/local_installers/cuda_11.4.0_470.42.01_linux.run"
    ;;
  11.5 )
    CUDA_VERSION="11.5.0"
    CUDA_INSTALLER_URL="https://developer.download.nvidia.com/compute/cuda/11.5.0/local_installers/cuda_11.5.0_495.29.05_linux.run"
    ;;
  11.5-aarch64 )
    CUDA_VERSION="11.5.0"
    CUDA_INSTALLER_URL="https://developer.download.nvidia.com/compute/cuda/11.5.0/local_installers/cuda_11.5.0_495.29.05_linux_sbsa.run"
    BASE_IMAGE="oraclelinux:8"
    IMAGE_SUFFIX="el8-aarch64"
    ;;
  11.6 )
    CUDA_VERSION="11.6.0"
    CUDA_INSTALLER_URL="https://developer.download.nvidia.com/compute/cuda/11.6.0/local_installers/cuda_11.6.0_510.39.01_linux.run"
    ;;
  11.6-aarch64 )
    CUDA_VERSION="11.6.0"
    CUDA_INSTALLER_URL="https://developer.download.nvidia.com/compute/cuda/11.6.0/local_installers/cuda_11.6.0_510.39.01_linux_sbsa.run"
    BASE_IMAGE="oraclelinux:8"
    IMAGE_SUFFIX="el8-aarch64"
    ;;
  11.7 )
    CUDA_VERSION="11.7.0"
    CUDA_INSTALLER_URL="https://developer.download.nvidia.com/compute/cuda/11.7.0/local_installers/cuda_11.7.0_515.43.04_linux.run"
    ;;
  11.7-aarch64 )
    CUDA_VERSION="11.7.0"
    CUDA_INSTALLER_URL="https://developer.download.nvidia.com/compute/cuda/11.7.0/local_installers/cuda_11.7.0_515.43.04_linux_sbsa.run"
    BASE_IMAGE="oraclelinux:8"
    IMAGE_SUFFIX="el8"
    ;;
  11.8 )
    CUDA_VERSION="11.8.0"
    CUDA_INSTALLER_URL="https://developer.download.nvidia.com/compute/cuda/11.8.0/local_installers/cuda_11.8.0_520.61.05_linux.run"
    ;;
  11.8-aarch64 )
    CUDA_VERSION="11.8.0"
    CUDA_INSTALLER_URL="https://developer.download.nvidia.com/compute/cuda/11.8.0/local_installers/cuda_11.8.0_520.61.05_linux_sbsa.run"
    BASE_IMAGE="oraclelinux:8"
    IMAGE_SUFFIX="el8"
    ;;
  12.0 )
    CUDA_VERSION="12.0.0"
    CUDA_INSTALLER_URL="https://developer.download.nvidia.com/compute/cuda/12.0.0/local_installers/cuda_12.0.0_525.60.13_linux.run"
    ;;
  12.0-aarch64 )
    CUDA_VERSION="12.0.0"
    CUDA_INSTALLER_URL="https://developer.download.nvidia.com/compute/cuda/12.0.0/local_installers/cuda_12.0.0_525.60.13_linux_sbsa.run"
    BASE_IMAGE="oraclelinux:8"
    IMAGE_SUFFIX="el8"
    ;;
  12.1 )
    CUDA_VERSION="12.1.0"
    CUDA_INSTALLER_URL="https://developer.download.nvidia.com/compute/cuda/12.1.0/local_installers/cuda_12.1.0_530.30.02_linux.run"
    ;;
  12.1-aarch64 )
    CUDA_VERSION="12.1.0"
    CUDA_INSTALLER_URL="https://developer.download.nvidia.com/compute/cuda/12.1.0/local_installers/cuda_12.1.0_530.30.02_linux_sbsa.run"
    BASE_IMAGE="oraclelinux:8"
    IMAGE_SUFFIX="el8"
    ;;

  * )
    echo "Unknown CUDA version: ${CUDA}"
    exit 1
    ;;
esac

export DOCKER_BUILDKIT=1
docker build -t "cupy/cupy-release-tools:cuda-runfile-${CUDA_VERSION}-${IMAGE_SUFFIX}" . \
    --build-arg BUILDKIT_INLINE_CACHE=1 \
    --build-arg BASE_IMAGE="${BASE_IMAGE}" \
    --build-arg CUDA_INSTALLER_URL="${CUDA_INSTALLER_URL}"

echo "Done. Run docker push cupy/cupy-release-tools:cuda-runfile-${CUDA_VERSION}-${IMAGE_SUFFIX} to push the image."
