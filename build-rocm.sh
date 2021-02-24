#!/bin/bash -uex

CUDA="${1}"
PYTHON="${2}"

# https://github.com/RadeonOpenCompute/ROCm#hardware-and-software-support
# https://rocmdocs.amd.com/en/latest/ROCm_Compiler_SDK/ROCm-Native-ISA.html#processors
export HCC_AMDGPU_TARGET=gfx801,gfx802,gfx803,gfx900,gfx906,gfx908,gfx1010,gfx1011,gfx1012

DIST_OPTIONS="--target wheel-linux --python ${PYTHON} --cuda ${CUDA}"
eval $(./get_dist_info.py ${DIST_OPTIONS} --source cupy)

./dist.py --action build  ${DIST_OPTIONS} --source cupy --output .
./dist.py --action verify ${DIST_OPTIONS} --dist ${DIST_FILE_NAME} --test release-tests/common --test release-tests/nccl
