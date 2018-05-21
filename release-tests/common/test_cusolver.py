import unittest

import cupy
import cupy.cuda.cusolver as libcusolver  # NOQA


class TestCusolver(unittest.TestCase):
    def test_enabled(self):
        assert cupy.cuda.cusolver_enabled
