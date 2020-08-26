#!/bin/bash -uex

CUDA="${1}"

mkdir -p nccl/
cd nccl

case ${CUDA} in
  sdist )
    curl -LO "https://developer.download.nvidia.com/compute/redist/nccl/v2.4/nccl_2.4.8-1+cuda9.2_x86_64.txz"
    ;;
  8.0 )
    curl -LO "https://developer.download.nvidia.com/compute/redist/nccl/v2.2/nccl_2.2.13-1+cuda8.0_x86_64.txz"
    ;;
  9.0 )
    curl -LO "https://developer.download.nvidia.com/compute/redist/nccl/v2.5/nccl_2.5.6-1+cuda9.0_x86_64.txz"
    ;;
  9.1 )
    curl -LO "https://developer.download.nvidia.com/compute/redist/nccl/v2.1/nccl_2.1.15-1+cuda9.1_x86_64.txz"
    ;;
  9.2 )
    curl -LO "https://developer.download.nvidia.com/compute/redist/nccl/v2.4/nccl_2.4.8-1+cuda9.2_x86_64.txz"
    ;;
  10.0 )
    curl -LO "https://developer.download.nvidia.com/compute/redist/nccl/v2.6/nccl_2.6.4-1+cuda10.0_x86_64.txz"
    ;;
  10.1 )
    curl -LO "https://developer.download.nvidia.com/compute/redist/nccl/v2.7/nccl_2.7.8-1+cuda10.1_x86_64.txz"
    ;;
  10.2 )
    curl -LO "https://developer.download.nvidia.com/compute/redist/nccl/v2.7/nccl_2.7.8-1+cuda10.2_x86_64.txz"
    ;;
  11.0 )
    curl -LO "https://developer.download.nvidia.com/compute/redist/nccl/v2.7/nccl_2.7.8-1+cuda11.0_x86_64.txz"
    ;;
  * )
    echo "Unsupported CUDA version: ${1}"
    exit 1
    ;;
esac
