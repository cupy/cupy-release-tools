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
        assert libnccl.get_version() == expected_version

    def test_cutensor(self):
        if cupy.cuda.runtime.runtimeGetVersion() < 10010:
            # cuTENSOR is only available for CUDA 10.1+.
            return
        if 13000 <= cupy.cuda.runtime.runtimeGetVersion():
            # TODO(kmaehashi): cuTENSOR is not yet available in CUDA 13+.
            return
        preload_version = self._get_config()['cutensor']['version']
        major, minor, patchlevel = (int(x) for x in preload_version.split('.'))
        expected_version = major * 10000 + minor * 100 + patchlevel
        assert libcutensor.available
        assert libcutensor.get_version() == expected_version
