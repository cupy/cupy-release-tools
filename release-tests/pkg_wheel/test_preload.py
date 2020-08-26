import unittest

import cupy
import cupy.cuda.cudnn as libcudnn


class TestPreload(unittest.TestCase):

    def test_cudnn(self):
        config = cupy._environment.get_preload_config()
        assert config is not None

        preload_version = config['cudnn']['version']
        major, minor, patchlevel = (int(x) for x in preload_version.split('.'))
        expected_version = major * 1000 + minor * 100 + patchlevel
        assert libcudnn.available
        assert libcudnn.get_build_version() == expected_version
        assert libcudnn.getVersion() == expected_version
