# -*- coding: utf-8 -*-

# Cython version to cythonize the code.
CYTHON_VERSION = '0.29.21'

# Key-value of sdist build settings.
# See descriptions of WHEEL_LINUX_CONFIGS for details.
# Note that cuDNN and NCCL must be available for sdist.
SDIST_CONFIG = {
    'image': 'nvidia/cuda:9.2-cudnn7-devel-centos6',
    'nccl': {
        'type': 'v2-tar',
        'files': [
            'nccl_2.4.8-1+cuda9.2_x86_64.txz',
        ],
    },
    'verify_image': 'nvidia/cuda:9.2-cudnn7-devel-{system}',
    'verify_systems': ['ubuntu18.04'],
}


# Key-value of CUDA version and its corresponding build settings.
# Keys of the build settings are as follows:
# - `name`: a package name
# - `image`: a name of the base docker image name used for build
# - `libs`: a list of shared libraries to be bundled in wheel
# - `nccl`: an assets of NCCL library distribution
# - `verify_image`: a name of the base docker image name used for verify
# - `verify_systems`: a list of systems to verify on; expaneded as {system} in
#                     `verify_image`.
WHEEL_LINUX_CONFIGS = {
    '7.0': {
        # Notes:
        # (1) NVIDIA does not provide CentOS 6 Docker image for CUDA 7.0.
        #     Therefore, the built wheel will not work on CentOS 6.
        # (2) NCCL is not available in CUDA 7.0.
        'name': 'cupy-cuda70',
        'image': 'nvidia/cuda:7.0-cudnn4-devel-centos7',
        'libs': [
            '/usr/local/cuda/lib64/libcudnn.so.4',  # cuDNN v4
        ],
        'includes': [
            ('/usr/local/cuda/include/cudnn.h', 'cudnn.h')
        ],
        'nccl': None,
        'verify_image': 'nvidia/cuda:7.0-devel-{system}',
        # 'verify_systems': ['ubuntu14.04', 'centos7'],
        'verify_systems': ['ubuntu14.04'],
    },
    '7.5': {
        'name': 'cupy-cuda75',
        'image': 'nvidia/cuda:7.5-cudnn6-devel-centos6',
        'libs': [
            '/usr/local/cuda/lib64/libcudnn.so.6',  # cuDNN v6
            '/usr/local/cuda/lib64/libnccl.so.1',  # NCCL v1
        ],
        'includes': [
            ('/usr/local/cuda/include/cudnn.h', 'cudnn.h')
        ],
        'nccl': {
            'type': 'v1-deb',
            'files': [
                'libnccl1_1.2.3-1.cuda7.5_amd64.deb',
                'libnccl-dev_1.2.3-1.cuda7.5_amd64.deb',
            ],
        },
        'verify_image': 'nvidia/cuda:7.5-devel-{system}',
        # 'verify_systems': ['ubuntu14.04', 'centos7', 'centos6'],
        'verify_systems': ['centos7'],
    },
    '8.0': {
        'name': 'cupy-cuda80',
        'image': 'nvidia/cuda:8.0-cudnn7-devel-centos6',
        'libs': [
            '/usr/local/cuda/lib64/libcudnn.so.7',  # cuDNN v7
            '/usr/local/cuda/lib64/libnccl.so.2',  # NCCL v2
        ],
        'includes': [
            ('/usr/local/cuda/include/cudnn.h', 'cudnn.h')
        ],
        'nccl': {
            'type': 'v2-tar',
            'files': [
                'nccl_2.2.13-1+cuda8.0_x86_64.txz',
            ],
        },
        'verify_image': 'nvidia/cuda:8.0-devel-{system}',
        # 'verify_systems': ['ubuntu16.04', 'ubuntu14.04',
        #                    'centos7', 'centos6'],
        'verify_systems': ['ubuntu16.04'],
    },
    '9.0': {
        'name': 'cupy-cuda90',
        'image': 'nvidia/cuda:9.0-cudnn7-devel-centos6',
        'libs': [
            '/usr/local/cuda/lib64/libcudnn.so.7',  # cuDNN v7
            '/usr/local/cuda/lib64/libnccl.so.2',  # NCCL v2
        ],
        'includes': [
            ('/usr/local/cuda/include/cudnn.h', 'cudnn.h')
        ],
        'nccl': {
            'type': 'v2-tar',
            'files': [
                'nccl_2.5.6-1+cuda9.0_x86_64.txz',
            ],
        },
        'verify_image': 'nvidia/cuda:9.0-devel-{system}',
        # 'verify_systems': ['ubuntu16.04', 'centos7', 'centos6'],
        'verify_systems': ['ubuntu16.04'],
    },
    '9.1': {
        'name': 'cupy-cuda91',
        'image': 'nvidia/cuda:9.1-cudnn7-devel-centos6',
        'libs': [
            '/usr/local/cuda/lib64/libcudnn.so.7',  # cuDNN v7
            '/usr/local/cuda/lib64/libnccl.so.2',  # NCCL v2
        ],
        'includes': [
            ('/usr/local/cuda/include/cudnn.h', 'cudnn.h')
        ],
        'nccl': {
            'type': 'v2-tar',
            'files': [
                'nccl_2.1.15-1+cuda9.1_x86_64.txz',
            ],
        },
        'verify_image': 'nvidia/cuda:9.1-devel-{system}',
        # 'verify_systems': ['ubuntu16.04', 'centos7', 'centos6'],
        'verify_systems': ['ubuntu16.04'],
    },
    '9.2': {
        'name': 'cupy-cuda92',
        'image': 'nvidia/cuda:9.2-cudnn7-devel-centos6',
        'libs': [
            '/usr/local/cuda/lib64/libcudnn.so.7',  # cuDNN v7
            '/usr/local/cuda/lib64/libnccl.so.2',  # NCCL v2
        ],
        'includes': [
            ('/usr/local/cuda/include/cudnn.h', 'cudnn.h')
        ],
        'nccl': {
            'type': 'v2-tar',
            'files': [
                'nccl_2.4.8-1+cuda9.2_x86_64.txz',
            ],
        },
        'verify_image': 'nvidia/cuda:9.2-devel-{system}',
        # 'verify_systems': ['ubuntu16.04', 'centos7', 'centos6'],
        'verify_systems': ['ubuntu16.04'],
    },
    '10.0': {
        'name': 'cupy-cuda100',
        'image': 'nvidia/cuda:10.0-cudnn7-devel-centos6',
        'libs': [
            '/usr/local/cuda/lib64/libcudnn.so.7',  # cuDNN v7
            '/usr/local/cuda/lib64/libnccl.so.2',  # NCCL v2
        ],
        'includes': [
            ('/usr/local/cuda/include/cudnn.h', 'cudnn.h')
        ],
        'nccl': {
            'type': 'v2-tar',
            'files': [
                'nccl_2.6.4-1+cuda10.0_x86_64.txz',
            ],
        },
        'verify_image': 'nvidia/cuda:10.0-devel-{system}',
        'verify_systems': ['ubuntu16.04'],
    },
    '10.1': {
        'name': 'cupy-cuda101',
        'image': 'nvidia/cuda:10.1-cudnn7-devel-centos6',
        'libs': [
            '/usr/local/cuda/lib64/libcudnn.so.7',  # cuDNN v7
            '/usr/local/cuda/lib64/libnccl.so.2',  # NCCL v2
        ],
        'includes': [
            ('/usr/local/cuda/include/cudnn.h', 'cudnn.h')
        ],
        'nccl': {
            'type': 'v2-tar',
            'files': [
                'nccl_2.7.8-1+cuda10.1_x86_64.txz',
            ],
        },
        'verify_image': 'nvidia/cuda:10.1-devel-{system}',
        'verify_systems': ['ubuntu16.04'],
    },
    '10.2': {
        'name': 'cupy-cuda102',
        'image': 'nvidia/cuda:10.2-cudnn7-devel-centos6',
        'libs': [
            '/usr/local/cuda/lib64/libcudnn.so.7',  # cuDNN v7
            '/usr/local/cuda/lib64/libnccl.so.2',  # NCCL v2
        ],
        'includes': [
            ('/usr/local/cuda/include/cudnn.h', 'cudnn.h')
        ],
        'nccl': {
            'type': 'v2-tar',
            'files': [
                'nccl_2.7.8-2+cuda10.2_x86_64.txz',
            ],
        },
        'verify_image': 'nvidia/cuda:10.2-devel-{system}',
        'verify_systems': ['ubuntu16.04'],
    },
    '11.0': {
        # Starting in CUDA 11.0, cuDNN is no longer bundled.
        'name': 'cupy-cuda110',
        # TODO(kmaehashi): Use the official image when released.
        'image': 'kmaehashi/cuda11-centos7:11.0-cudnn8-devel-centos7',
        'libs': [
            '/usr/local/cuda/lib64/libnccl.so.2',  # NCCL v2
        ],
        'includes': [],
        'nccl': {
            'type': 'v2-tar',
            'files': [
                'nccl_2.7.8-1+cuda11.0_x86_64.txz',
            ],
        },

        # Note: Using image with cuDNN 8 preinstalled.
        'verify_image': 'nvidia/cuda:11.0-cudnn8-runtime-{system}',
        'verify_systems': ['ubuntu18.04'],
    },

}


WHEEL_WINDOWS_CONFIGS = {
    '8.0': {
        'name': 'cupy-cuda80',
        'libs': [
            'cudnn64_7.dll',  # cuDNN v7
            'nvToolsExt64_1.dll',  # NVIDIA Tools Extension Library
        ],
        'cudart_lib': 'cudart64_80',
        'check_version': lambda x: 8000 <= x < 9000,
    },
    '9.0': {
        'name': 'cupy-cuda90',
        'libs': [
            'cudnn64_7.dll',  # cuDNN v7
            'nvToolsExt64_1.dll',  # NVIDIA Tools Extension Library
        ],
        'cudart_lib': 'cudart64_90',
        'check_version': lambda x: 9000 <= x < 9010,
    },
    '9.1': {
        'name': 'cupy-cuda91',
        'libs': [
            'cudnn64_7.dll',  # cuDNN v7
            'nvToolsExt64_1.dll',  # NVIDIA Tools Extension Library
        ],
        'cudart_lib': 'cudart64_91',
        'check_version': lambda x: 9010 <= x < 9020,
    },
    '9.2': {
        'name': 'cupy-cuda92',
        'libs': [
            'cudnn64_7.dll',  # cuDNN v7
            'nvToolsExt64_1.dll',  # NVIDIA Tools Extension Library
        ],
        'cudart_lib': 'cudart64_92',
        'check_version': lambda x: 9020 <= x < 9030,
    },
    '10.0': {
        'name': 'cupy-cuda100',
        'libs': [
            'cudnn64_7.dll',  # cuDNN v7
            'nvToolsExt64_1.dll',  # NVIDIA Tools Extension Library
        ],
        'cudart_lib': 'cudart64_100',
        'check_version': lambda x: 10000 <= x < 10010,
    },
    '10.1': {
        'name': 'cupy-cuda101',
        'libs': [
            'cudnn64_7.dll',  # cuDNN v7
            'nvToolsExt64_1.dll',  # NVIDIA Tools Extension Library
        ],
        'cudart_lib': 'cudart64_101',
        'check_version': lambda x: 10010 <= x < 10020,
    },
    '10.2': {
        'name': 'cupy-cuda102',
        'libs': [
            'cudnn64_7.dll',  # cuDNN v7
            'nvToolsExt64_1.dll',  # NVIDIA Tools Extension Library
        ],
        'cudart_lib': 'cudart64_102',
        'check_version': lambda x: 10020 <= x < 10030,
    },
    '11.0': {
        'name': 'cupy-cuda110',
        'libs': [
            'nvToolsExt64_1.dll',  # NVIDIA Tools Extension Library
        ],
        'cudart_lib': 'cudart64_110',
        'check_version': lambda x: 11000 <= x < 11010,
    },
}


_long_description_header = '''\
.. image:: https://raw.githubusercontent.com/cupy/cupy/master/docs/image/cupy_logo_1000px.png
   :width: 400

CuPy : NumPy-like API accelerated with CUDA
===========================================

`CuPy <https://cupy.chainer.org/>`_ is an implementation of NumPy-compatible multi-dimensional array on CUDA.

'''  # NOQA


# Long description of the sdist package in reST syntax.
SDIST_LONG_DESCRIPTION = _long_description_header + '''\
This package (``cupy``) is a source distribution.
For most users, use of pre-build wheel distributions are recommended:

- `cupy-cuda102 <https://pypi.org/project/cupy-cuda102/>`_ (for CUDA 10.2)
- `cupy-cuda101 <https://pypi.org/project/cupy-cuda101/>`_ (for CUDA 10.1)
- `cupy-cuda100 <https://pypi.org/project/cupy-cuda100/>`_ (for CUDA 10.0)
- `cupy-cuda92 <https://pypi.org/project/cupy-cuda92/>`_ (for CUDA 9.2)
- `cupy-cuda91 <https://pypi.org/project/cupy-cuda91/>`_ (for CUDA 9.1)
- `cupy-cuda90 <https://pypi.org/project/cupy-cuda90/>`_ (for CUDA 9.0)
- `cupy-cuda80 <https://pypi.org/project/cupy-cuda80/>`_ (for CUDA 8.0)

Please see `Installation Guide <https://docs-cupy.chainer.org/en/latest/install.html>`_ for the detailed instructions.
'''  # NOQA


# Long description of the wheel package in reST syntax.
# `{cuda}` will be replaced by the CUDA version (e.g., `9.0`).
WHEEL_LONG_DESCRIPTION = _long_description_header + '''\
This is a CuPy wheel (precompiled binary) package for CUDA {cuda}.
You need to install `CUDA Toolkit {cuda} <https://developer.nvidia.com/cuda-toolkit-archive>`_ to use these packages.

If you have another version of CUDA, please see `Installation Guide <https://docs-cupy.chainer.org/en/latest/install.html>`_ for instructions.
If you want to build CuPy from `source distribution <https://pypi.python.org/pypi/cupy>`_, use ``pip install cupy`` instead.
'''  # NOQA

# Key-value of python version (used in pyenv) to use for build and its
# corresponding configurations.
# Keys of the configuration are as follows:
# - `python_tag`: a CPython implementation tag
# - `abi_tag`: a CPython ABI tag
# - `requires`: a list of required packages; this is needed as some older
#               NumPy does not support newer Python.
WHEEL_PYTHON_VERSIONS = {
    '3.5.1': {
        'python_tag': 'cp35',
        'abi_tag': 'cp35m',
        'requires': [],
    },
    '3.6.0': {
        'python_tag': 'cp36',
        'abi_tag': 'cp36m',
        'requires': [],
    },
    '3.7.0': {
        'python_tag': 'cp37',
        'abi_tag': 'cp37m',
        'requires': [],
    },
    '3.8.0': {
        'python_tag': 'cp38',
        'abi_tag': 'cp38',
        'requires': [],
    },
}

# Python versions available for verification.
VERIFY_PYTHON_VERSIONS = sorted(list(WHEEL_PYTHON_VERSIONS.keys()))

# Sorted list of all possible python versions used in build process.
PYTHON_VERSIONS = sorted(set(
    list(WHEEL_PYTHON_VERSIONS.keys()) +
    VERIFY_PYTHON_VERSIONS
))
