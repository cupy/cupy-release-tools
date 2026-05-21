from __future__ import annotations

import sys
import unittest

import cupy
import cupy.cuda.cutensor as libcutensor
import cupy.cuda.nccl as libnccl


class TestPreload(unittest.TestCase):

    def _get_config(self):
        config = cupy._environment.get_preload_config()
        assert config is not None
        return config

    def test_nccl(self):
        if sys.platform == 'win32':
            # NCCL is not available on Windows.
            return
        preload_version = self._get_config()['nccl']['version']
        major, minor, patchlevel = (int(x) for x in preload_version.split('.'))
        major_mult = 1000
        if (2, 9) <= (major, minor):
            # NCCL 2.9 shows version as 20908 instead of 2908
            major_mult = 10000
        expected_version = major * major_mult + minor * 100 + patchlevel
        assert libnccl.available
        assert libnccl.get_build_version() == expected_version
        # Note: Previously build-time version and runtime version were same,
        # because we preferred preloading NCCL from ~/.cupy/cuda_libs installed
        # by install_library.py tool. However, starting CuPy v14.0.0, NCCL
        # version at runtime depends on NCCL installed on host, because
        # cuda-pathfinder is now the primary method to discover libraries.
        # assert libnccl.get_version() == expected_version

    def test_cutensor(self):
        if cupy.cuda.runtime.runtimeGetVersion() < 10010:
            # cuTENSOR is only available for CUDA 10.1+.
            return
        preload_version = self._get_config()['cutensor']['version']
        major, minor, patchlevel = (int(x) for x in preload_version.split('.'))
        expected_version = major * 10000 + minor * 100 + patchlevel
        assert libcutensor.available
        # Note: cuda-pathfinder does not yet support libcutensor.
        assert libcutensor.get_version() == expected_version
