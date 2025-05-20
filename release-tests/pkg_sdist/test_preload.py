from __future__ import annotations
import unittest

import cupy


class TestPreload(unittest.TestCase):

    def test_preload_config(self):
        config = cupy._environment.get_preload_config()
        assert config is None
