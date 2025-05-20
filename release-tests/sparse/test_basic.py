from __future__ import annotations
import unittest

import cupy
import cupyx


class TestCuSparse(unittest.TestCase):
    # Separated from common tests as ROCm build does not support cuSPARSE yet.
    def test_csr(self):
        m = cupy.array([[0, 1, 0, 2],
                        [0, 0, 0, 0],
                        [0, 0, 3, 0]], dtype=cupy.float32)
        cupyx.scipy.sparse.csr_matrix(m)
