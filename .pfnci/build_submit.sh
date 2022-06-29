#!/bin/bash

# Submit as FlexCI jobs

set -u

BRANCH="$(cat ./.pfnci/BRANCH)"
JOB_GROUP="$(date +"%F_%T")"

echo "JOB_GROUP = ${JOB_GROUP}"
echo "URL (Linux) = https://console.cloud.google.com/storage/browser/tmp-asia-pfn-public-ci/cupy-release-tools/build-linux/${JOB_GROUP}_${BRANCH}/"
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

# sdist
submit_job cupy-wheel-linux ".pfnci/wheel-linux/main.sh sdist 3.7 ${BRANCH} ${JOB_GROUP}"

# wheels (Linux)
for CUDA in 10.2 11.0 11.1 11.2 11.3 11.4 11.5 11.6 11.7; do
  submit_job cupy-wheel-linux ".pfnci/wheel-linux/main.sh ${CUDA} 3.7,3.8,3.9,3.10 ${BRANCH} ${JOB_GROUP}"
done

# wheels (Windows)
for CUDA in 10.2 11.0 11.1 11.2 11.3 11.4 11.5 11.6 11.7; do
  for PYTHON in 3.7 3.8 3.9 3.10; do
    submit_job cupy-wheel-win ".pfnci\\wheel-windows\\main.bat ${CUDA} ${PYTHON} ${BRANCH} ${JOB_GROUP}"
  done
done

echo "Check status with:"
echo "./.pfnci/build_status.py ${job_ids[@]}"
