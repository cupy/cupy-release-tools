#!/bin/bash

set -uex

PYTHON="$1"
CUDA="$2"
BRANCH="$3"

# Download NCCL
./download_nccl.sh "${CUDA}"
ls -al nccl

# Clone CuPy
git clone --recursive https://github.com/cupy/cupy.git cupy
git -C cupy checkout "origin/${BRANCH}"

# Build and Verify
./build.sh "${CUDA}" "${PYTHON}"
