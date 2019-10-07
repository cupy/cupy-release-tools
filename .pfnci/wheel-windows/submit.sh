#!/bin/sh -uex

# Submit as FlexCI jobs
for PYTHON in 3.6.0 3.7.0; do
  for CUDA in 8.0 9.0 9.1 9.2 10.0 10.1; do
    for BRANCH in origin/master origin/v6; do
      imosci --project=cupy-wheel-win run ".pfnci\\wheel-windows\\main.bat ${PYTHON} ${CUDA} ${BRANCH}"
    done
  done
done
