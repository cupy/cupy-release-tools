import unittest

import cupy
import cupy.cuda.cudnn as libcudnn
import cupy.cuda.cutensor as libcutensor
import cupy.cuda.nccl as libnccl


class TestPreload(unittest.TestCase):

    def _get_config(self):
        config = cupy._environment.get_preload_config()
        assert config is not None
        return config

    def test_cudnn(self):
        preload_version = self._get_config()['cudnn']['version']
        major, minor, patchlevel = (int(x) for x in preload_version.split('.'))
        expected_version = major * 1000 + minor * 100 + patchlevel
        assert libcudnn.available
        assert libcudnn.get_build_version() == expected_version
        assert libcudnn.getVersion() == expected_version

    def test_nccl(self):
        preload_version = self._get_config()['nccl']['version']
        major, minor, patchlevel = (int(x) for x in preload_version.split('.'))
        expected_version = major * 1000 + minor * 100 + patchlevel
        assert libnccl.available
        assert libnccl.get_build_version() == expected_version
        assert libnccl.get_version() == expected_version

    def test_cutensor(self):
        if cupy.cuda.runtime.runtimeGetVersion() < 10010:
            # cuTENSOR is only available for CUDA 10.1+.
            return
        preload_version = self._get_config()['cutensor']['version']
        major, minor, patchlevel = (int(x) for x in preload_version.split('.'))
        expected_version = major * 1000 + minor * 100 + patchlevel
        assert libcutensor.available
        assert libcutensor.get_version() == expected_version
