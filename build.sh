#!/bin/bash -uex

CUDA="${1}"
PYTHON="${2}"

# Set DIST_OPTIONS and DIST_FILE_NAME
case ${CUDA} in
  sdist )
    DIST_OPTIONS="--target sdist --python ${PYTHON}"
    eval $(./get_dist_info.py --target sdist --source cupy)
    ;;
  * )
    DIST_OPTIONS="--target wheel-linux --python ${PYTHON} --cuda ${CUDA}"
    eval $(./get_dist_info.py --target wheel-linux --source cupy --cuda ${CUDA} --python ${PYTHON})
    ;;
esac

# Set VERIFY_ARGS
VERIFY_ARGS="--test release-tests/common"
case ${CUDA} in
  sdist )
    # CUDA (sdist)
    VERIFY_ARGS="${VERIFY_ARGS} --test release-tests/sparse --test release-tests/nccl --test release-tests/pkg_sdist"
    ;;
  rocm-* )
    # ROCm (wheel)
    VERIFY_ARGS="${VERIFY_ARGS}"
    ;;
  13.x )
    # CUDA 13.x (wheel)
    VERIFY_ARGS="${VERIFY_ARGS} --test release-tests/sparse --test release-tests/nccl --test release-tests/pkg_wheel"
    ;;
  * )
    # CUDA (wheel)
    VERIFY_ARGS="${VERIFY_ARGS} --test release-tests/sparse --test release-tests/nccl --test release-tests/pkg_wheel"
    ;;
esac

# Set additional environment variables
case ${CUDA} in
  rocm-* )
    # https://github.com/RadeonOpenCompute/ROCm#hardware-and-software-support
    # https://rocmdocs.amd.com/en/latest/ROCm_Compiler_SDK/ROCm-Native-ISA.html#processors
    export HCC_AMDGPU_TARGET=gfx908,gfx90a,gfx942,gfx950,gfx1030,gfx1100,gfx1101,gfx1200,gfx1201
    ;;
  * )
    ;;
esac

./dist.py --action build  ${DIST_OPTIONS} --source cupy --output .

if [[ "${CUPY_RELEASE_SKIP_VERIFY:-0}" != "1" ]]; then
  if [[ "${CUPY_RELEASE_VERIFY_REMOVE_IMAGE:-0}" = "1" ]]; then
    VERIFY_ARGS="${VERIFY_ARGS} --rmi"
  fi
  python3 -m twine check --strict "${DIST_FILE_NAME}"
  ./dist.py --action verify ${DIST_OPTIONS} --dist ${DIST_FILE_NAME} ${VERIFY_ARGS}
fi
