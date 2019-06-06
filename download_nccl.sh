#!/bin/bash -uex

CUDA="${1}"

mkdir -p nccl/
case ${CUDA} in
  sdist )
    wget -O "nccl/nccl_2.1.4-1+cuda9.0_x86_64.txz" "https://s3-ap-northeast-1.amazonaws.com/pfn-internal-public/cupy/nccl_2.1.4-1%2Bcuda9.0_x86_64.txz"
    ;;
  7.0 )
    echo "NCCL is not supported in CUDA 7.0"
    exit 1
    ;;
  7.5 )
    wget -O "nccl/libnccl1_1.2.3-1.cuda7.5_amd64.deb" "https://github.com/NVIDIA/nccl/releases/download/v1.2.3-1%2Bcuda7.5/libnccl1_1.2.3-1.cuda7.5_amd64.deb"
    wget -O "nccl/libnccl-dev_1.2.3-1.cuda7.5_amd64.deb" "https://github.com/NVIDIA/nccl/releases/download/v1.2.3-1%2Bcuda7.5/libnccl-dev_1.2.3-1.cuda7.5_amd64.deb"
    ;;
  8.0 )
    wget -O "nccl/nccl_2.2.13-1+cuda8.0_x86_64.txz" "https://s3-ap-northeast-1.amazonaws.com/pfn-internal-public/cupy/nccl_2.2.13-1%2Bcuda8.0_x86_64.txz"
    ;;
  9.0 )
    wget -O "nccl/nccl_2.3.7-1+cuda9.0_x86_64.txz" "https://s3-ap-northeast-1.amazonaws.com/pfn-internal-public/cupy/nccl_2.3.7-1%2Bcuda9.0_x86_64.txz"
    ;;
  9.1 )
    wget -O "nccl/nccl_2.1.15-1+cuda9.1_x86_64.txz" "https://s3-ap-northeast-1.amazonaws.com/pfn-internal-public/cupy/nccl_2.1.15-1%2Bcuda9.1_x86_64.txz"
    ;;
  9.2 )
    wget -O "nccl/nccl_2.4.2-1+cuda9.2_x86_64.txz" "https://s3-ap-northeast-1.amazonaws.com/pfn-internal-public/cupy/nccl_2.4.2-1%2Bcuda9.2_x86_64.txz"
    ;;
  10.0 )
    wget -O "nccl/nccl_2.4.2-1+cuda10.0_x86_64.txz" "https://s3-ap-northeast-1.amazonaws.com/pfn-internal-public/cupy/nccl_2.4.2-1%2Bcuda10.0_x86_64.txz"
    ;;
  10.1 )
    wget -O "nccl/nccl_2.4.2-1+cuda10.1_x86_64.txz" "https://s3-ap-northeast-1.amazonaws.com/pfn-internal-public/cupy/nccl_2.4.2-1%2Bcuda10.1_x86_64.txz"
    ;;
  * )
    echo "Unsupported CUDA version: ${1}"
    exit 1
    ;;
esac
