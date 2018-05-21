import unittest

import cupy
import cupy.cuda.thrust as libthrust  # NOQA


class TestThrust(unittest.TestCase):
    def test_enabled(self):
        assert cupy.cuda.thrust_enabled
