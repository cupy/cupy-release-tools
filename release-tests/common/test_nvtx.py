import unittest

import cupy.cuda.nvtx as libnvtx


class TestNVTX(unittest.TestCase):
    def test_nvtx(self):
        libnvtx.Mark('Test')
