# -*- coding: utf-8 -*-

# Cython version to cythonize the code.
CYTHON_VERSION = '0.29.21'

# Key-value of sdist build settings.
# See descriptions of WHEEL_LINUX_CONFIGS for details.
SDIST_CONFIG = {
    'image': 'nvidia/cuda:9.2-devel-centos6',
    'nccl': {
        'type': 'v2-tar',
        'files': [
            'nccl_2.4.8-1+cuda9.2_x86_64.txz',
        ],
    },
    'verify_image': 'nvidia/cuda:9.2-cudnn7-devel-{system}',
    'verify_systems': ['ubuntu18.04'],
    'verify_preloads': [],
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
    '9.0': {
        'name': 'cupy-cuda90',
        'image': 'nvidia/cuda:9.0-devel-centos6',
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
        # Note: using devel as NVRTC not working in CUDA 9.0 runtime image
        'verify_image': 'nvidia/cuda:9.0-devel-{system}',
        # 'verify_systems': ['ubuntu16.04', 'centos7', 'centos6'],
        'verify_systems': ['ubuntu16.04'],
        'verify_preloads': [],
    },
    '9.2': {
        'name': 'cupy-cuda92',
        'image': 'nvidia/cuda:9.2-devel-centos6',
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
        'verify_image': 'nvidia/cuda:9.2-runtime-{system}',
        # 'verify_systems': ['ubuntu16.04', 'centos7', 'centos6'],
        'verify_systems': ['ubuntu16.04'],
        'verify_preloads': [],
    },
    '10.0': {
        'name': 'cupy-cuda100',
        'image': 'nvidia/cuda:10.0-devel-centos6',
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
        'verify_preloads': [],
    },
    '10.1': {
        'name': 'cupy-cuda101',
        'image': 'nvidia/cuda:10.1-devel-centos6',
        'libs': [
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
        'verify_image': 'nvidia/cuda:10.1-runtime-{system}',
        'verify_systems': ['ubuntu16.04'],
        'verify_preloads': ['cudnn'],
    },
    '10.2': {
        'name': 'cupy-cuda102',
        'image': 'nvidia/cuda:10.2-devel-centos6',
        'libs': [
            '/usr/local/cuda/lib64/libnccl.so.2',  # NCCL v2
        ],
        'includes': [
            ('/usr/local/cuda/include/cudnn.h', 'cudnn.h')
        ],
        'nccl': {
            'type': 'v2-tar',
            'files': [
                'nccl_2.7.8-1+cuda10.2_x86_64.txz',
            ],
        },
        'verify_image': 'nvidia/cuda:10.2-runtime-{system}',
        'verify_systems': ['ubuntu16.04'],
        'verify_preloads': ['cudnn'],
    },
    '11.0': {
        'name': 'cupy-cuda110',
        # TODO(kmaehashi): Use the official image when released.
        'image': 'kmaehashi/cuda11-centos7:11.0-devel-centos7',
        'libs': [
            '/usr/local/cuda/lib64/libnccl.so.2',  # NCCL v2
        ],
        'includes': [
            ('/usr/local/cuda/include/cudnn.h', 'cudnn.h')
        ],
        'nccl': {
            'type': 'v2-tar',
            'files': [
                'nccl_2.7.8-1+cuda11.0_x86_64.txz',
            ],
        },
        'verify_image': 'nvidia/cuda:11.0-runtime-{system}',
        'verify_systems': ['ubuntu18.04'],
        'verify_preloads': ['cudnn'],
    },
    '11.1': {
        'name': 'cupy-cuda111',
        'image': 'nvidia/cuda:11.1-devel-centos7',
        'libs': [
            '/usr/local/cuda/lib64/libnccl.so.2',  # NCCL v2
        ],
        'includes': [
            ('/usr/local/cuda/include/cudnn.h', 'cudnn.h')
        ],
        'nccl': {
            'type': 'v2-tar',
            'files': [
                'nccl_2.7.8-1+cuda11.1_x86_64.txz',
            ],
        },
        'verify_image': 'nvidia/cuda:11.1-runtime-{system}',
        'verify_systems': ['ubuntu18.04'],
        'verify_preloads': ['cudnn'],
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
            'nvToolsExt64_1.dll',  # NVIDIA Tools Extension Library
        ],
        'cudart_lib': 'cudart64_101',
        'check_version': lambda x: 10010 <= x < 10020,
    },
    '10.2': {
        'name': 'cupy-cuda102',
        'libs': [
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
    '11.1': {
        'name': 'cupy-cuda111',
        'libs': [
            'nvToolsExt64_1.dll',  # NVIDIA Tools Extension Library
        ],
        'cudart_lib': 'cudart64_111',
        'check_version': lambda x: 11010 <= x < 11020,
    },
}


_long_description_header = '''\
.. image:: https://raw.githubusercontent.com/cupy/cupy/master/docs/image/cupy_logo_1000px.png
   :width: 400

CuPy : A NumPy-compatible array library accelerated by CUDA
===========================================================

`CuPy <https://cupy.dev/>`_ is an implementation of NumPy-compatible multi-dimensional array on CUDA.

'''  # NOQA


# Long description of the sdist package in reST syntax.
SDIST_LONG_DESCRIPTION = _long_description_header + '''\
This package (``cupy``) is a source distribution.
For most users, use of pre-build wheel distributions are recommended:

- `cupy-cuda111 <https://pypi.org/project/cupy-cuda111/>`_ (for CUDA 11.1)
- `cupy-cuda110 <https://pypi.org/project/cupy-cuda110/>`_ (for CUDA 11.0)
- `cupy-cuda102 <https://pypi.org/project/cupy-cuda102/>`_ (for CUDA 10.2)
- `cupy-cuda101 <https://pypi.org/project/cupy-cuda101/>`_ (for CUDA 10.1)
- `cupy-cuda100 <https://pypi.org/project/cupy-cuda100/>`_ (for CUDA 10.0)
- `cupy-cuda92 <https://pypi.org/project/cupy-cuda92/>`_ (for CUDA 9.2)
- `cupy-cuda90 <https://pypi.org/project/cupy-cuda90/>`_ (for CUDA 9.0)

Please see `Installation Guide <https://docs.cupy.dev/en/latest/install.html>`_ for the detailed instructions.
'''  # NOQA


# Long description of the wheel package in reST syntax.
# `{cuda}` will be replaced by the CUDA version (e.g., `9.0`).
WHEEL_LONG_DESCRIPTION = _long_description_header + '''\
This is a CuPy wheel (precompiled binary) package for CUDA {cuda}.
You need to install `CUDA Toolkit {cuda} <https://developer.nvidia.com/cuda-toolkit-archive>`_ to use these packages.

If you have another version of CUDA, or want to build from source, refer to the `Installation Guide <https://docs.cupy.dev/en/latest/install.html>`_ for instructions.
'''  # NOQA

# Key-value of python version (used in pyenv) to use for build and its
# corresponding configurations.
# Keys of the configuration are as follows:
# - `python_tag`: a CPython implementation tag
# - `abi_tag`: a CPython ABI tag
# - `requires`: a list of required packages; this is needed as some older
#               NumPy does not support newer Python.
WHEEL_PYTHON_VERSIONS = {
    '3.5.3': {
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
