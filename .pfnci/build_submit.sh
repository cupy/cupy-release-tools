#!/bin/bash

# Submit as FlexCI jobs

set -u

BRANCH="$(cat ./.pfnci/BRANCH)"
JOB_GROUP="$(date +"%F_%T")"

echo "JOB_GROUP = ${JOB_GROUP}"
echo "URL (Windows) = https://console.cloud.google.com/storage/browser/tmp-asia-pfn-public-ci/cupy-release-tools/build-windows/${JOB_GROUP}_${BRANCH}/"

job_ids=()
submit_job() {
  local project="$1"
  local command="$2"
  echo "Job: ${command}"
  local submit_output=$(imosci --config=pfn-public-ci --project=${project} run "${command}")
  local submit_status=$?
  echo "-> ${submit_output}"

  if [[ ${submit_status} -ne 0 ]]; then
    echo "Job submission failed!"
    exit 1
  fi

  # Extract Job ID part from output: "Status: https://ci.preferred.jp/r/job/76261"
  job_ids+=($(basename "${submit_output}"))
}

# wheels (Windows)
for CUDA in 11.x 12.x 13.x; do
  for PYTHON in 3.10 3.11 3.12 3.13; do
    submit_job cupy-wheel-win ".pfnci\\wheel-windows\\main.bat ${CUDA} ${PYTHON} ${BRANCH} ${JOB_GROUP}"
  done
done

echo "Check status with:"
echo "./.pfnci/build_status.py ${job_ids[@]}"
