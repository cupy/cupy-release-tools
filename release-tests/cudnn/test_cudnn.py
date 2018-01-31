import unittest

import cupy
import cupy.cuda.cudnn as libcudnn
import cupy.cudnn


class TestCuDNN(unittest.TestCase):
    def test_relu(self):
        x = cupy.arange(12, dtype=cupy.float32).reshape(3, 4)
        cupy.cudnn.activation_forward(x, libcudnn.CUDNN_ACTIVATION_RELU)
