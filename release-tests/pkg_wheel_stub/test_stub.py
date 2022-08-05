import sys
import unittest

import cupy
import cupyx


class TestStub(unittest.TestCase):

    def test_public_apis_reference(self):
        print(cupy.ndarray)
        print(cupy.ufunc)

        @cupy.fuse()
        def test1(x):
            pass

        @cupy.memoize()
        def test2(x):
            pass

        @cupyx.jit.rawkernel()
        def test3(x):
            pass
