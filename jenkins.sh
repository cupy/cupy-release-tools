#!/bin/bash -uex

# This script is expected to be called from Jenkins.
# The following environment variables expected to be set:
# - CUDA (CUDA verseion; 7.0, 7.5, etc. or sdist)
# - PYTHON (python version; 2.7.6, 3.6.0, etc.)
# This script also expects that `cupy` source tree exists in the same directory.

###
### Build & Verify Distribution
###

./build.sh "${CUDA}" "${PYTHON}"
