#!/bin/bash

# Submit as FlexCI jobs

set -u

BRANCH="v9"
JOB_GROUP="$(date +"%F_%T")"

echo "JOB_GROUP = ${JOB_GROUP}"
echo "URL = https://console.cloud.google.com/storage/browser/tmp-asia-pfn-public-ci/cupy-release-tools/build-linux/${JOB_GROUP}_${BRANCH}/"

job_ids=()
submit_job() {
  local command="$1"
  echo "Job: ${command}"
  local submit_output=$(imosci --config=pfn-public-ci --project=cupy-wheel-linux run "${command}")
  local submit_status=$?
  echo "-> ${submit_output}"

  if [[ ${submit_status} -ne 0 ]]; then
    echo "Job submission failed!"
    exit 1
  fi

  # Extract Job ID part from output: "Status: https://ci.preferred.jp/r/job/76261"
  job_ids+=($(basename "${submit_output}"))
}

submit_job ".pfnci/wheel-linux/main.sh 3.7.0 sdist ${BRANCH} ${JOB_GROUP}"
for CUDA in 9.2 10.0 10.1 10.2 11.0 11.1 11.2 11.3 11.4; do
  for PYTHON in 3.6 3.7 3.8 3.9; do
    submit_job ".pfnci/wheel-linux/main.sh ${PYTHON} ${CUDA} ${BRANCH} ${JOB_GROUP}"
  done
done

echo "Check status with:"
echo "./.pfnci/build_status.py ${job_ids[@]}"
