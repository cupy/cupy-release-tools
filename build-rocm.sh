#!/bin/bash -uex

CUDA="${1}"
PYTHON="${2}"

if [ "${HCC_AMDGPU_TARGET:-}" = "" ]; then
    echo "*** HCC_AMDGPU_TARGET is not set, verification will fail"
fi

DIST_OPTIONS="--target wheel-linux --python ${PYTHON} --cuda ${CUDA}"
eval $(./get_dist_info.py ${DIST_OPTIONS} --source cupy)

./dist.py --action build  ${DIST_OPTIONS} --source cupy --output .
./dist.py --action verify ${DIST_OPTIONS} --dist ${DIST_FILE_NAME} --test release-tests/common
