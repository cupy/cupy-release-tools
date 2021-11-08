# -*- coding: utf-8 -*-

# CuPy major version supported by this tool.
CUPY_MAJOR_VERSION = '9'

# Cython version to cythonize the code.
CYTHON_VERSION = '0.29.22'

# Key-value of sdist build settings.
# See descriptions of WHEEL_LINUX_CONFIGS for details.
SDIST_CONFIG = {
    'image': 'nvidia/cuda:9.2-devel-centos6',
    # This image contains cuDNN and NCCL.
    'verify_image': 'nvidia/cuda:10.0-cudnn7-devel-{system}',
    'verify_systems': ['ubuntu18.04'],
}


# Key-value of CUDA version and its corresponding build settings for Linux.
# Keys of the build settings are as follows:
# - `name`: a package name
# - `kind`: type of the package (`cuda` or `rocm`)
# - `platform_version`: alternate name of the `kind` platform version used
#                       for long description
# - `image`: a name of the base docker image name used for build
# - `libs`: a list of shared libraries to be bundled in wheel
# - `includes`: a list of header files to be bundled in wheel
# - `preloads`: optional CUDA libraries to be used
# - `verify_image`: a name of the base docker image name used for verify
# - `verify_systems`: a list of systems to verify on; expaneded as {system} in
#                     `verify_image`.
# - `system_packages`: a string of depending library names expanded into the
#                      package manager command.
WHEEL_LINUX_CONFIGS = {
    '9.2': {
        'name': 'cupy-cuda92',
        'kind': 'cuda',
        'image': 'nvidia/cuda:9.2-devel-centos6',
        'libs': [
        ],
        'includes': [
        ],
        'preloads': ['nccl', 'cudnn'],
        'verify_image': 'nvidia/cuda:9.2-runtime-{system}',
        # 'verify_systems': ['ubuntu16.04', 'centos7', 'centos6'],
        'verify_systems': ['ubuntu16.04'],
        'system_packages': '',
    },
    '10.0': {
        'name': 'cupy-cuda100',
        'kind': 'cuda',
        'image': 'nvidia/cuda:10.0-devel-centos6',
        'libs': [
        ],
        'includes': [
        ],
        'preloads': ['nccl', 'cudnn'],
        'verify_image': 'nvidia/cuda:10.0-devel-{system}',
        'verify_systems': ['ubuntu16.04'],
        'system_packages': '',
    },
    '10.1': {
        'name': 'cupy-cuda101',
        'kind': 'cuda',
        'image': 'nvidia/cuda:10.1-devel-centos6',
        'libs': [
        ],
        'includes': [
        ],
        'preloads': ['cutensor', 'nccl', 'cudnn'],
        'verify_image': 'nvidia/cuda:10.1-runtime-{system}',
        'verify_systems': ['ubuntu16.04'],
        'system_packages': '',
    },
    '10.2': {
        'name': 'cupy-cuda102',
        'kind': 'cuda',
        'image': 'nvidia/cuda:10.2-devel-centos6',
        'libs': [
        ],
        'includes': [
        ],
        'preloads': ['cutensor', 'nccl', 'cudnn'],
        'verify_image': 'nvidia/cuda:10.2-runtime-{system}',
        'verify_systems': ['ubuntu16.04'],
        'system_packages': '',
    },
    '11.0': {
        'name': 'cupy-cuda110',
        'kind': 'cuda',
        'image': 'cupy/cupy-release-tools:cuda-runfile-11.0.2-centos7',
        'libs': [
        ],
        'includes': [
        ],
        'preloads': ['cutensor', 'nccl', 'cudnn'],
        'verify_image': 'nvidia/cuda:11.0-runtime-{system}',
        'verify_systems': ['ubuntu18.04'],
        'system_packages': '',
    },
    '11.1': {
        'name': 'cupy-cuda111',
        'kind': 'cuda',
        'image': 'cupy/cupy-release-tools:cuda-runfile-11.1.0-centos7',
        'libs': [
        ],
        'includes': [
        ],
        'preloads': ['cutensor', 'nccl', 'cudnn'],
        'verify_image': 'nvidia/cuda:11.1-runtime-{system}',
        'verify_systems': ['ubuntu18.04'],
        'system_packages': '',
    },
    '11.2': {
        'name': 'cupy-cuda112',
        'kind': 'cuda',
        'image': 'cupy/cupy-release-tools:cuda-runfile-11.2.0-centos7',
        'libs': [
        ],
        'includes': [
        ],
        'preloads': ['cutensor', 'nccl', 'cudnn'],
        'verify_image': 'nvidia/cuda:11.2.1-runtime-{system}',
        'verify_systems': ['ubuntu18.04'],
        'system_packages': '',
    },
    '11.3': {
        'name': 'cupy-cuda113',
        'kind': 'cuda',
        'image': 'cupy/cupy-release-tools:cuda-runfile-11.3.0-centos7',
        'libs': [],
        'includes': [],
        'preloads': ['cutensor', 'nccl', 'cudnn'],
        'verify_image': 'nvidia/cuda:11.3.0-runtime-{system}',
        'verify_systems': ['ubuntu18.04'],
        'system_packages': '',
    },
    '11.4': {
        'name': 'cupy-cuda114',
        'kind': 'cuda',
        'image': 'cupy/cupy-release-tools:cuda-runfile-11.4.0-centos7',
        'libs': [],
        'includes': [],
        'preloads': ['cutensor', 'nccl', 'cudnn'],
        'verify_image': 'nvidia/cuda:11.4.0-runtime-{system}',
        'verify_systems': ['ubuntu18.04'],
        'system_packages': '',
    },
    '11.5': {
        'name': 'cupy-cuda115',
        'kind': 'cuda',
        'image': 'cupy/cupy-release-tools:cuda-runfile-11.5.0-centos7',
        'libs': [],
        'includes': [],
        'preloads': ['cutensor', 'nccl', 'cudnn'],
        # TODO(kmaehashi): use NVIDIA docker image after released
        'verify_image': 'cupy/cupy-release-tools:cuda-runfile-11.5.0-centos7',
        'verify_systems': ['default'],
        'system_packages': '',
    },
    'rocm-4.0': {
        'name': 'cupy-rocm-4-0',
        'kind': 'rocm',
        'platform_version': '4.0',
        'image': 'rocm/dev-centos-7:4.0.1',
        'libs': [],
        'includes': [],
        'preloads': [],
        'verify_image': 'rocm/rocm-terminal:4.0',
        'verify_systems': ['default'],
        'system_packages': 'rocm-dev hipblas hipsparse rocsparse rocrand rocthrust rocsolver rocfft hipcub rocprim rccl'  # NOQA
    },
    'rocm-4.2': {
        'name': 'cupy-rocm-4-2',
        'kind': 'rocm',
        'platform_version': '4.2',
        'image': 'rocm/dev-centos-7:4.2',
        'libs': [],
        'includes': [],
        'preloads': [],
        'verify_image': 'rocm/rocm-terminal:4.2',
        'verify_systems': ['default'],
        'system_packages': 'rocm-dev hipblas hipfft hipsparse rocsparse rocrand rocthrust rocsolver rocfft hipcub rocprim rccl'  # NOQA
    },
    'rocm-4.3': {
        'name': 'cupy-rocm-4-3',
        'kind': 'rocm',
        'platform_version': '4.3',
        'image': 'rocm/dev-centos-7:4.3',
        'libs': [],
        'includes': [],
        'preloads': [],
        'verify_image': 'rocm/rocm-terminal:4.3',
        'verify_systems': ['default'],
        'system_packages': 'rocm-dev hipblas hipfft hipsparse rocsparse rocrand rocthrust rocsolver rocfft hipcub rocprim rccl'  # NOQA
    },
}

# Key-value of CUDA version and its corresponding build settings for Windows.
# Keys of the build settings are as follows:
# - `name`: a package name
# - `libs`: a list of DLLs to be bundled in wheel
# - `cudart_lib`: name of CUDA Runtime DLL
# - `check_version`: a function to check if the CUDA version is correct.
WHEEL_WINDOWS_CONFIGS = {
    '9.2': {
        'name': 'cupy-cuda92',
        'kind': 'cuda',
        'libs': [
            'nvToolsExt64_1.dll',  # NVIDIA Tools Extension Library
        ],
        'preloads': ['cudnn'],
        'cudart_lib': 'cudart64_92',
        'check_version': lambda x: 9020 <= x < 9030,
    },
    '10.0': {
        'name': 'cupy-cuda100',
        'kind': 'cuda',
        'libs': [
            'nvToolsExt64_1.dll',  # NVIDIA Tools Extension Library
        ],
        'preloads': ['cudnn'],
        'cudart_lib': 'cudart64_100',
        'check_version': lambda x: 10000 <= x < 10010,
    },
    '10.1': {
        'name': 'cupy-cuda101',
        'kind': 'cuda',
        'libs': [
            'nvToolsExt64_1.dll',  # NVIDIA Tools Extension Library
        ],
        'preloads': ['cutensor', 'cudnn'],
        'cudart_lib': 'cudart64_101',
        'check_version': lambda x: 10010 <= x < 10020,
    },
    '10.2': {
        'name': 'cupy-cuda102',
        'kind': 'cuda',
        'libs': [
            'nvToolsExt64_1.dll',  # NVIDIA Tools Extension Library
        ],
        'preloads': ['cutensor', 'cudnn'],
        'cudart_lib': 'cudart64_102',
        'check_version': lambda x: 10020 <= x < 10030,
    },
    '11.0': {
        'name': 'cupy-cuda110',
        'kind': 'cuda',
        'libs': [
            'nvToolsExt64_1.dll',  # NVIDIA Tools Extension Library
        ],
        'preloads': ['cutensor', 'cudnn'],
        'cudart_lib': 'cudart64_110',
        'check_version': lambda x: 11000 <= x < 11010,
    },
    '11.1': {
        'name': 'cupy-cuda111',
        'kind': 'cuda',
        'libs': [
            'nvToolsExt64_1.dll',  # NVIDIA Tools Extension Library
        ],
        'preloads': ['cutensor', 'cudnn'],
        'cudart_lib': 'cudart64_110',  # binary compatible between CUDA 11.x
        'check_version': lambda x: 11010 <= x < 11020,
    },
    '11.2': {
        'name': 'cupy-cuda112',
        'kind': 'cuda',
        'libs': [
            'nvToolsExt64_1.dll',  # NVIDIA Tools Extension Library
        ],
        'preloads': ['cutensor', 'cudnn'],
        'cudart_lib': 'cudart64_110',  # binary compatible between CUDA 11.x
        'check_version': lambda x: 11020 <= x < 11030,
    },
    '11.3': {
        'name': 'cupy-cuda113',
        'kind': 'cuda',
        'libs': [
            'nvToolsExt64_1.dll',  # NVIDIA Tools Extension Library
        ],
        'preloads': ['cutensor', 'cudnn'],
        'cudart_lib': 'cudart64_110',  # binary compatible between CUDA 11.x
        'check_version': lambda x: 11030 <= x < 11040,
    },
    '11.4': {
        'name': 'cupy-cuda114',
        'kind': 'cuda',
        'libs': [
            'nvToolsExt64_1.dll',  # NVIDIA Tools Extension Library
        ],
        'preloads': ['cutensor', 'cudnn'],
        'cudart_lib': 'cudart64_110',  # binary compatible between CUDA 11.x
        'check_version': lambda x: 11040 <= x < 11050,
    },
    '11.5': {
        'name': 'cupy-cuda115',
        'kind': 'cuda',
        'libs': [
            'nvToolsExt64_1.dll',  # NVIDIA Tools Extension Library
        ],
        'preloads': ['cutensor', 'cudnn'],
        'cudart_lib': 'cudart64_110',  # binary compatible between CUDA 11.x
        'check_version': lambda x: 11050 <= x < 11060,
    },
}


_long_description_header = '''\
.. image:: https://raw.githubusercontent.com/cupy/cupy/master/docs/image/cupy_logo_1000px.png
   :width: 400

CuPy : NumPy & SciPy for GPU
============================

`CuPy <https://cupy.dev/>`_ is a NumPy/SciPy-compatible array library for GPU-accelerated computing with Python.

'''  # NOQA


# Long description of the sdist package in reST syntax.
SDIST_LONG_DESCRIPTION = _long_description_header + '''\
This package (``cupy``) is a source distribution.
For most users, use of pre-build wheel distributions are recommended:

- `cupy-cuda115 <https://pypi.org/project/cupy-cuda115/>`_ (for CUDA 11.5)
- `cupy-cuda114 <https://pypi.org/project/cupy-cuda114/>`_ (for CUDA 11.4)
- `cupy-cuda113 <https://pypi.org/project/cupy-cuda113/>`_ (for CUDA 11.3)
- `cupy-cuda112 <https://pypi.org/project/cupy-cuda112/>`_ (for CUDA 11.2)
- `cupy-cuda111 <https://pypi.org/project/cupy-cuda111/>`_ (for CUDA 11.1)
- `cupy-cuda110 <https://pypi.org/project/cupy-cuda110/>`_ (for CUDA 11.0)
- `cupy-cuda102 <https://pypi.org/project/cupy-cuda102/>`_ (for CUDA 10.2)
- `cupy-cuda101 <https://pypi.org/project/cupy-cuda101/>`_ (for CUDA 10.1)
- `cupy-cuda100 <https://pypi.org/project/cupy-cuda100/>`_ (for CUDA 10.0)
- `cupy-cuda92 <https://pypi.org/project/cupy-cuda92/>`_ (for CUDA 9.2)
- `cupy-cuda90 <https://pypi.org/project/cupy-cuda90/>`_ (for CUDA 9.0)

- `cupy-rocm-4-3 <https://pypi.org/project/cupy-rocm-4-3/>`_ (for ROCm 4.3)
- `cupy-rocm-4-2 <https://pypi.org/project/cupy-rocm-4-2/>`_ (for ROCm 4.2)
- `cupy-rocm-4-0 <https://pypi.org/project/cupy-rocm-4-0/>`_ (for ROCm 4.0)

Please see `Installation Guide <https://docs.cupy.dev/en/latest/install.html>`_ for the detailed instructions.
'''  # NOQA


# Long description of the CUDA wheel package in reST syntax.
# `{version}` will be replaced by the CUDA version (e.g., `9.0`).
WHEEL_LONG_DESCRIPTION_CUDA = _long_description_header + '''\
This is a CuPy wheel (precompiled binary) package for CUDA {version}.
You need to install `CUDA Toolkit {version} <https://developer.nvidia.com/cuda-toolkit-archive>`_ to use these packages.

If you have another version of CUDA, or want to build from source, refer to the `Installation Guide <https://docs.cupy.dev/en/latest/install.html>`_ for instructions.
'''  # NOQA


# Long description of the ROCm wheel package in reST syntax.
# `{version}` will be replaced by the ROCm version (e.g., `4.0`).
WHEEL_LONG_DESCRIPTION_ROCM = _long_description_header + '''\
This is a CuPy wheel (precompiled binary) package for AMD ROCm {version}.
You need to install `ROCm {version} <https://rocmdocs.amd.com/en/latest/Installation_Guide/Installation-Guide.html>`_ to use these packages.

If you have another version of ROCm, or want to build from source, refer to the `Installation Guide <https://docs.cupy.dev/en/latest/install.html>`_ for instructions.
'''  # NOQA


# Key-value of python version to use for build and its
# corresponding configurations.
# Keys of the configuration are as follows:
# - `pyenv`: a full CPython version to use (only effective for Linux builds)
# - `python_tag`: a CPython implementation tag
# - `abi_tag`: a CPython ABI tag
WHEEL_PYTHON_VERSIONS = {
    '3.6': {
        'pyenv': '3.6.14',
        'python_tag': 'cp36',
        'abi_tag': 'cp36m',
    },
    '3.7': {
        'pyenv': '3.7.11',
        'python_tag': 'cp37',
        'abi_tag': 'cp37m',
    },
    '3.8': {
        'pyenv': '3.8.11',
        'python_tag': 'cp38',
        'abi_tag': 'cp38',
    },
    '3.9': {
        'pyenv': '3.9.0',
        'python_tag': 'cp39',
        'abi_tag': 'cp39',
    },
}
