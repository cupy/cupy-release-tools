import unittest

import cupy.cuda


class TestCusolver(unittest.TestCase):
    def test_enabled(self):
        assert cupy.cuda.cusolver_enabled

    def test_available(self):
        assert cupy.cuda.cusolver is not None
