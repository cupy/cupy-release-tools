#!/bin/bash

set -uex

PYTHON=$1
CUDA=$2
BRANCH=$3
JOB_GROUP=${4:-}

git clone --recursive --branch "${BRANCH}" --depth 1 https://github.com/cupy/cupy.git cupy

./download_nccl.sh "${CUDA}"
./build.sh "${CUDA}" "${PYTHON}"

if [ -z "${JOB_GROUP}" ]; then
    echo "Upload skipped as JOB_GROUP is not specified"
else
    gsutil -m cp $(find . -maxdepth 1 -type f -name "cupy_*.whl" -or -name "cupy-*.tar.gz")  gs://tmp-asia-pfn-public-ci/cupy-release-tools/build-linux/${JOB_GROUP}_${BRANCH}/${FLEXCI_JOB_ID:-0}_py${PYTHON}_cuda${CUDA}/
fi
