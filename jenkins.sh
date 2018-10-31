#!/bin/bash -uex

# This script is expected to be called from Jenkins.
# The following environment variables expected to be set:
# - CUDA (CUDA verseion; 7.0, 7.5, etc. or sdist)
# - PYTHON (python version; 2.7.6, 3.6.0, etc.)
# - NVGET_USER (Username for nvget)
# - NVGET_PASSWORD (Password for nvget)
# This script also expects that `cupy` source tree exists in the same directory.

NVGET="docker run --rm -e NVGET_USER -e NVGET_PASSWORD -u ${UID} -v ${PWD}:/download kmaehashi/nvget"

###
### Prepare NCCL assets
###

rm -rf nccl
mkdir -p nccl

HAVE_NCCL="yes"

# Avoid downloading NCCL assets in parallel.
NVGET_DELAY="$(( ${RANDOM} % 20 ))"
echo "Waiting for ${NVGET_DELAY} seconds before start..."
sleep "${NVGET_DELAY}"

case ${CUDA} in
  sdist )
    $NVGET --output "nccl/nccl_2.1.4-1+cuda9.0_x86_64.txz" "https://developer.nvidia.com/compute/machine-learning/nccl/secure/v2.1/prod/nccl_2.1.4-1cuda9.0_x86_64"
    ;;
  7.0 )
    HAVE_NCCL="no"
    ;;
  7.5 )
    wget -O "nccl/libnccl1_1.2.3-1.cuda7.5_amd64.deb" "https://github.com/NVIDIA/nccl/releases/download/v1.2.3-1%2Bcuda7.5/libnccl1_1.2.3-1.cuda7.5_amd64.deb"
    wget -O "nccl/libnccl-dev_1.2.3-1.cuda7.5_amd64.deb" "https://github.com/NVIDIA/nccl/releases/download/v1.2.3-1%2Bcuda7.5/libnccl-dev_1.2.3-1.cuda7.5_amd64.deb"
    ;;
  8.0 )
    $NVGET --output "nccl/nccl_2.2.13-1+cuda8.0_x86_64.txz" "https://developer.nvidia.com/compute/machine-learning/nccl/secure/v2.2/prod/nccl_2.2.13-1_cuda8.0_x86_64"
    ;;
  9.0 )
    $NVGET --output "nccl/nccl_2.2.13-1+cuda9.0_x86_64.txz" "https://developer.nvidia.com/compute/machine-learning/nccl/secure/v2.2/prod/nccl_2.2.13-1_cuda9.0_x86_64"
    ;;
  9.1 )
    $NVGET --output "nccl/nccl_2.1.15-1+cuda9.1_x86_64.txz" "https://developer.nvidia.com/compute/machine-learning/nccl/secure/v2.1/prod/nccl_2.1.15-1cuda9.1_x86_64"
    ;;
  9.2 )
    $NVGET --output "nccl/nccl_2.2.13-1+cuda9.2_x86_64.txz" "https://developer.nvidia.com/compute/machine-learning/nccl/secure/v2.2/prod/nccl_2.2.13-1_cuda9.2_x86_64"
    ;;
  10.0 )
    $NVGET --output "nccl/nccl_2.3.5-2+cuda10.0_x86_64.txz" "https://developer.nvidia.com/compute/machine-learning/nccl/secure/v2.3/prod2/CUDA10.0/txz/nccl_2.3.5-2-cuda10.0_x86_64"
    ;;
  * )
    exit 1
    ;;
esac

###
### Build & Verify Distribution
###

# Set DIST_OPTIONS and DIST_FILE_NAME
case ${CUDA} in
  sdist )
    DIST_OPTIONS="--target sdist --nccl-assets nccl --python ${PYTHON}"
    eval $(./get_dist_info.py --target sdist --source cupy)
    ;;
  * )
    DIST_OPTIONS="--target wheel-linux --nccl-assets nccl --python ${PYTHON} --cuda ${CUDA}"
    eval $(./get_dist_info.py --target wheel-linux --source cupy --cuda ${CUDA} --python ${PYTHON})
    ;;
esac

./dist.py --action build ${DIST_OPTIONS} --source cupy --output .

VERIFY_ARGS="--test release-tests/common --test release-tests/cudnn"
if [ ! "${HAVE_NCCL}" = "no" ]; then
  VERIFY_ARGS="${VERIFY_ARGS} --test release-tests/nccl"
fi

./dist.py --action verify ${DIST_OPTIONS} --dist ${DIST_FILE_NAME} ${VERIFY_ARGS}
