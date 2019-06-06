#!/bin/bash -uex

CUDA="${1}"
PYTHON="${2}"
HAVE_NCCL="${3:-yes}"

# Set DIST_OPTIONS and DIST_FILE_NAME
case ${CUDA} in
  sdist )
    DIST_OPTIONS="--target sdist --nccl-assets nccl --python ${PYTHON}"
    eval $(./get_dist_info.py --target sdist --source cupy)
    ;;
  * )
    DIST_OPTIONS="--target wheel-linux --nccl-assets nccl --python ${PYTHON} --cuda ${CUDA}"
    eval $(./get_dist_info.py --target wheel-linux --source cupy --cuda ${CUDA} --python ${PYTHON})
    ;;
esac

VERIFY_ARGS="--test release-tests/common --test release-tests/cudnn"
if [ "${HAVE_NCCL}" = "yes" ]; then
  VERIFY_ARGS="${VERIFY_ARGS} --test release-tests/nccl"
fi

./dist.py --action build  ${DIST_OPTIONS} --source cupy --output .
./dist.py --action verify ${DIST_OPTIONS} --dist ${DIST_FILE_NAME} ${VERIFY_ARGS}

