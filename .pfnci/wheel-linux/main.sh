#!/bin/bash

set -uex

CUDA=$1
PYTHON=$2
BRANCH=${3:-}
JOB_GROUP=${4:-}

gcloud auth configure-docker || echo "Failed to configure access to GCR"

if [ -z "${BRANCH}" ]; then
    BRANCH="$(cat ./.pfnci/BRANCH)"
fi

git clone --recursive --branch "${BRANCH}" --depth 1 https://github.com/cupy/cupy.git cupy

cupy/.pfnci/linux/update-cuda-driver.sh

python3 -m pip install -r ./requirements.txt

for PY in $(echo ${PYTHON} | tr ',' ' '); do
    CUPY_RELEASE_VERIFY_REMOVE_IMAGE=1 ./build.sh "${CUDA}" "${PY}"
done

if [ -z "${JOB_GROUP}" ]; then
    echo "Upload skipped as JOB_GROUP is not specified"
else
    gsutil -m cp $(find . -maxdepth 1 -type f -name "cupy_*.whl" -or -name "cupy-*.tar.gz") gs://tmp-asia-pfn-public-ci/cupy-release-tools/build-linux/${JOB_GROUP}_${BRANCH}/${FLEXCI_JOB_ID:-0}_py${PYTHON}_cuda${CUDA}/
fi
