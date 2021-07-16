#!/bin/sh -uex

# Submit as FlexCI jobs

BRANCH="master"
JOB_GROUP="$(date +"%F_%T")"

echo "JOB_GROUP = ${JOB_GROUP}"

echo "URL = https://console.cloud.google.com/storage/browser/tmp-asia-pfn-public-ci/cupy-release-tools/build-windows/${JOB_GROUP}_${BRANCH}/"
for CUDA in 10.0 10.1 10.2 11.0 11.1 11.2 11.3 11.4; do
  for PYTHON in 3.6.0 3.7.0 3.8.0 3.9.0; do
    imosci --project=cupy-wheel-win run ".pfnci\\wheel-windows\\main.bat ${PYTHON} ${CUDA} ${BRANCH} ${JOB_GROUP}"
  done
done
