#!/bin/sh -uex

# Submit as FlexCI jobs

BRANCH="master"
JOB_GROUP="$(date +"%F_%T")"

echo "JOB_GROUP = ${JOB_GROUP}"

echo "URL = https://console.cloud.google.com/storage/browser/tmp-asia-pfn-public-ci/cupy-release-tools/build-linux/${JOB_GROUP}_${BRANCH}/"
imosci --project=cupy-wheel-linux run ".pfnci/wheel-linux/main.sh 3.7.0 sdist ${BRANCH} ${JOB_GROUP}"
for CUDA in 10.0 10.1 10.2 11.0 11.1 11.2 11.3; do
  for PYTHON in 3.6.0 3.7.0 3.8.0 3.9.0; do
    imosci --project=cupy-wheel-linux run ".pfnci/wheel-linux/main.sh ${PYTHON} ${CUDA} ${BRANCH} ${JOB_GROUP}"
  done
done
