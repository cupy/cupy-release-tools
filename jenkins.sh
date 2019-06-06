#!/bin/bash -uex

# This script is expected to be called from Jenkins.
# The following environment variables expected to be set:
# - CUDA (CUDA verseion; 7.0, 7.5, etc. or sdist)
# - PYTHON (python version; 2.7.6, 3.6.0, etc.)
# This script also expects that `cupy` source tree exists in the same directory.

###
### Prepare NCCL assets
###

HAVE_NCCL="no"
if [ "${CUDA}" != "7.0" ]; then
  HAVE_NCCL="yes"
  ./download_nccl.sh "${CUDA}"
fi

###
### Build & Verify Distribution
###

./build.sh "${CUDA}" "${PYTHON}" "${HAVE_NCCL}"
