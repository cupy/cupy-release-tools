#!/bin/bash

set -uex

CUDA="$1"
IMAGE_SUFFIX="el8"
BASE_IMAGE="oraclelinux:8"
PLATFORM="linux/amd64"

case ${CUDA} in
  12.9 )
    CUDA_VERSION="12.9.0"
    CUDA_INSTALLER_URL="https://developer.download.nvidia.com/compute/cuda/12.9.0/local_installers/cuda_12.9.0_575.51.03_linux.run"
    ;;
  12.9-aarch64 )
    CUDA_VERSION="12.9.0"
    CUDA_INSTALLER_URL="https://developer.download.nvidia.com/compute/cuda/12.9.0/local_installers/cuda_12.9.0_575.51.03_linux_sbsa.run"
    PLATFORM="linux/arm64"
    ;;
  13.0 )
    CUDA_VERSION="13.0.0"
    CUDA_INSTALLER_URL="https://developer.download.nvidia.com/compute/cuda/13.0.0/local_installers/cuda_13.0.0_580.65.06_linux.run"
    ;;
  13.0-aarch64 )
    CUDA_VERSION="13.0.0"
    CUDA_INSTALLER_URL="https://developer.download.nvidia.com/compute/cuda/13.0.0/local_installers/cuda_13.0.0_580.65.06_linux_sbsa.run"
    PLATFORM="linux/arm64"
    ;;

  * )
    echo "Unknown CUDA version: ${CUDA}"
    exit 1
    ;;
esac

export DOCKER_BUILDKIT=1
docker buildx build --platform "${PLATFORM}" -t "cupy/cupy-release-tools:cuda-runfile-${CUDA_VERSION}-${IMAGE_SUFFIX}" . \
    --build-arg BUILDKIT_INLINE_CACHE=1 \
    --build-arg BASE_IMAGE="${BASE_IMAGE}" \
    --build-arg CUDA_INSTALLER_URL="${CUDA_INSTALLER_URL}"

PUSH_COMMAND="docker push cupy/cupy-release-tools:cuda-runfile-${CUDA_VERSION}-${IMAGE_SUFFIX}"

echo "Done."

if [[ ${AUTO_PUSH:-0} == 1 ]]; then
  echo "Pushing: ${PUSH_COMMAND}"
  eval "${PUSH_COMMAND}"
else
  echo "Run ${PUSH_COMMAND} to push the image."
fi
