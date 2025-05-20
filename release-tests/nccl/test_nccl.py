from __future__ import annotations

import unittest

import cupy.cuda.nccl as libnccl


class TestNCCL(unittest.TestCase):
    def test_nccl(self):
        uid = libnccl.get_unique_id()
        comm = libnccl.NcclCommunicator(1, uid, 0)  # NOQA
