import unittest

import cupy
import cupy.cuda.cusolver as libcusolver


class TestCusolver(unittest.TestCase):
    def test_enabled(self):
        assert cupy.cuda.cusolver_enabled
