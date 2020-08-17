#!/bin/bash -uex

CUDA="9.2"
PYTHON="3.8.0"

# Download NCCL
./download_nccl.sh "${CUDA}"
ls -al nccl

# Clone CuPy
git clone --recursive https://github.com/cupy/cupy.git cupy

# Build and Verify
./build.sh "${CUDA}" "${PYTHON}"
