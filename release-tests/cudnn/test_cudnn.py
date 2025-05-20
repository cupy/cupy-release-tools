from __future__ import annotations
import unittest

import cupy
import cupy.cuda.cudnn as libcudnn
import cupy.cudnn


class TestCuDNN(unittest.TestCase):
    def test_relu(self):
        # Testing in REVERSE order of library dependency.

        # cudnn_adv_train
        libcudnn.createCTCLossDescriptor()

        # cudnn_adv_infer
        libcudnn.createRNNDataDescriptor()

        # cudnn_cnn_train
        libcudnn.createFusedOpsPlan(
            libcudnn.CUDNN_FUSED_SCALE_BIAS_ACTIVATION_CONV_BNSTATS)

        # cudnn_cnn_infer
        # libcudnn.convolutionForward
        x = cupy.random.uniform(0, 1, (10, 3, 30, 40)).astype(cupy.float32)
        W = cupy.random.uniform(0, 1, (1, 3, 10, 10)).astype(cupy.float32)
        b = cupy.random.uniform(0, 1, (1,)).astype(cupy.float32)
        y = cupy.random.uniform(0, 1, (10, 1, 7, 6)).astype(cupy.float32)
        cupy.cudnn.convolution_forward(
            x, W, b, y, (5, 5), (5, 7), (1, 1), 1,
            auto_tune=False, tensor_core='never')

        # cudnn_ops_train
        # libcudnn.activationBackward
        x = cupy.arange(12, dtype=cupy.float32).reshape(3, 4)
        y = cupy.arange(12, dtype=cupy.float32).reshape(3, 4)
        gy = cupy.arange(12, dtype=cupy.float32).reshape(3, 4)
        cupy.cudnn.activation_backward(
            x, y, gy, libcudnn.CUDNN_ACTIVATION_RELU)

        # cudnn_ops_infer
        # libcudnn.activationForward
        x = cupy.arange(12, dtype=cupy.float32).reshape(3, 4)
        cupy.cudnn.activation_forward(x, libcudnn.CUDNN_ACTIVATION_RELU)
