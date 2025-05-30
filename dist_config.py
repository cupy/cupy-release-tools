from __future__ import annotations

from typing import TYPE_CHECKING, Literal, TypedDict

if TYPE_CHECKING:
    from collections.abc import Callable

    # Can be imported from typing for >= 3.11
    from typing_extensions import NotRequired

# CuPy major version supported by this tool.
CUPY_MAJOR_VERSION = '13'

# Tools to be used for build.
CYTHON_VERSION = '3.0.12'
FASTRLOCK_VERSION = '0.8.3'


class _SDistConfig(TypedDict):
    image: str
    verify_image: str
    verify_systems: list[str]


# Key-value of sdist build settings.
# See descriptions of WHEEL_LINUX_CONFIGS for details.
SDIST_CONFIG: _SDistConfig = {
    'image': 'nvidia/cuda:11.2.2-devel-centos7',
    # This image contains cuDNN and NCCL.
    'verify_image': 'nvidia/cuda:11.4.3-cudnn8-devel-{system}',
    'verify_systems': ['ubuntu18.04'],
}


class _WheelLinuxConfig(TypedDict):
    name: str
    kind: Literal['cuda', 'rocm']
    arch: NotRequired[str]
    platform_version: str
    image: str
    libs: list[str]
    includes: list[tuple[str, str]]
    preloads: list[str]
    builder_dockerfile: NotRequired[str]
    verify_image: str
    verify_systems: list[str]
    system_packages: str


# Key-value of CUDA version and its corresponding build settings for Linux.
# Keys of the build settings are as follows:
# - `name`: a package name
# - `kind`: type of the package (`cuda` or `rocm`)
# - `arch`: platform for the package (optional, default: `x86_64`)
# - `platform_version`: alternate name of the `kind` platform version used
#                       for long description (optional, defualt: dict key)
# - `image`: a name of the base docker image name used for build
# - `libs`: a list of shared libraries to be bundled in wheel
# - `includes`: a list of header files to be bundled in wheel
# - `preloads`: optional CUDA libraries to be used
# - `verify_image`: a name of the base docker image name used for verify
# - `verify_systems`: a list of systems to verify on; expaneded as {system} in
#                     `verify_image`.
# - `system_packages`: a string of depending library names expanded into the
#                      package manager command.
WHEEL_LINUX_CONFIGS: dict[str, _WheelLinuxConfig] = {
    '11.x': {
        # CUDA Enhanced Compatibility wheel (for CUDA 11.2~11.x)
        'name': 'cupy-cuda11x',
        'kind': 'cuda',
        'platform_version': '11.2 - 11.8',
        # Use the latest CUDA version for build.
        'image': 'cupy/cupy-release-tools:cuda-runfile-11.8.0-centos7',
        'libs': [],
        'includes': [],
        'preloads': ['cutensor', 'nccl', 'cudnn'],
        'verify_image': 'nvidia/cuda:{system}',
        'verify_systems': [
            # Test on all supported CUDA version variants.
            '11.2.2-runtime-ubuntu18.04',
            '11.3.1-runtime-ubuntu18.04',
            '11.4.3-runtime-ubuntu18.04',
            '11.5.2-runtime-ubuntu18.04',
            '11.6.2-runtime-ubuntu18.04',
            '11.7.1-runtime-ubuntu18.04',
            '11.8.0-runtime-ubuntu18.04',
        ],
        'system_packages': '',
    },
    '11.x-aarch64': {
        # CUDA Enhanced Compatibility wheel (for CUDA 11.2~11.x)
        'name': 'cupy-cuda11x',
        'kind': 'cuda',
        'arch': 'aarch64',
        'platform_version': '11.2 - 11.8',
        # Use the latest image.
        'image': 'cupy/cupy-release-tools:cuda-runfile-11.8.0-el8',
        'libs': [],
        'includes': [],
        'preloads': ['nccl'],
        'builder_dockerfile': 'Dockerfile.el8',
        'verify_image': 'nvidia/cuda:{system}',
        'verify_systems': [
            # Test on all supported CUDA version variants.
            '11.2.2-runtime-ubi8',
            '11.3.1-runtime-ubi8',
            '11.4.3-runtime-ubi8',
            '11.5.2-runtime-ubi8',
            '11.6.2-runtime-ubi8',
            '11.7.1-runtime-ubi8',
            '11.8.0-runtime-ubi8',
        ],
        'system_packages': '',
    },
    '12.x': {
        # CUDA Enhanced Compatibility wheel (for CUDA 12.x)
        'name': 'cupy-cuda12x',
        'kind': 'cuda',
        'platform_version': '12.x',
        # Use the latest CUDA version for build.
        # Note: CUDA 12 still supports RHEL/CentOS 7 on x86_64
        'image': 'cupy/cupy-release-tools:cuda-runfile-12.8.0-centos7',
        'libs': [],
        'includes': [],
        'preloads': ['cutensor', 'nccl', 'cudnn'],
        'verify_image': 'nvidia/cuda:{system}',
        'verify_systems': [
            # Test on all supported CUDA version variants.
            '12.0.1-runtime-ubuntu18.04',
            '12.1.1-runtime-ubuntu22.04',
            '12.2.0-runtime-ubuntu22.04',
            '12.3.0-runtime-ubuntu22.04',
            '12.4.0-runtime-ubuntu22.04',
            '12.5.0-runtime-ubuntu22.04',
            '12.6.0-runtime-ubuntu22.04',
            '12.8.0-runtime-ubuntu22.04',
        ],
        'system_packages': '',
    },
    '12.x-aarch64': {
        # CUDA Enhanced Compatibility wheel (for CUDA 12.x)
        'name': 'cupy-cuda12x',
        'kind': 'cuda',
        'arch': 'aarch64',
        'platform_version': '12.x',
        # Use the latest image.
        'image': 'cupy/cupy-release-tools:cuda-runfile-12.8.0-el8',
        'libs': [],
        'includes': [],
        'preloads': ['nccl'],
        'builder_dockerfile': 'Dockerfile.el8',
        'verify_image': 'nvidia/cuda:{system}',
        'verify_systems': [
            # Test on all supported CUDA version variants.
            '12.0.1-runtime-ubi8',
            '12.1.1-runtime-ubi8',
            '12.2.0-runtime-ubi8',
            '12.3.0-runtime-ubi8',
            '12.4.0-runtime-ubi8',
            '12.5.0-runtime-ubi8',
            '12.6.0-runtime-ubi8',
            '12.8.0-runtime-ubi8',
        ],
        'system_packages': '',
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
    'rocm-5.0': {
        'name': 'cupy-rocm-5-0',
        'kind': 'rocm',
        'platform_version': '5.0',
        'image': 'rocm/dev-centos-7:5.0',
        'libs': [],
        'includes': [],
        'preloads': [],
        'verify_image': 'rocm/rocm-terminal:5.0',
        'verify_systems': ['default'],
        'system_packages': 'rocm-hip-sdk hip-runtime-amd roctracer-dev'  # NOQA
    },
}


class _WheelWindowsConfig(TypedDict):
    name: str
    kind: Literal['cuda']
    libs: list[str]
    preloads: list[str]
    cudart_lib: str
    check_version: Callable[[int], bool]


# Key-value of CUDA version and its corresponding build settings for Windows.
# Keys of the build settings are as follows:
# - `name`: a package name
# - `libs`: a list of DLLs to be bundled in wheel
# - `cudart_lib`: name of CUDA Runtime DLL
# - `check_version`: a function to check if the CUDA version is correct.
WHEEL_WINDOWS_CONFIGS: dict[str, _WheelWindowsConfig] = {
    '11.x': {
        # CUDA Enhanced Compatibility wheel (for CUDA 11.2~11.x)
        'name': 'cupy-cuda11x',
        'kind': 'cuda',
        'libs': [],
        'preloads': ['cutensor', 'cudnn'],
        'cudart_lib': 'cudart64_110',  # binary compatible between CUDA 11.x
        'check_version': lambda x: 11080 <= x < 11090,  # CUDA 11.8
    },
    '12.x': {
        # CUDA Enhanced Compatibility wheel (for CUDA 12.x)
        'name': 'cupy-cuda12x',
        'kind': 'cuda',
        'libs': [],
        'preloads': ['cutensor', 'cudnn'],
        'cudart_lib': 'cudart64_12',  # binary compatible between CUDA 12.x
        'check_version': lambda x: 12080 <= x < 12090,  # CUDA 12.8
    }
}


_long_description_header = '''\
.. image:: https://raw.githubusercontent.com/cupy/cupy/main/docs/image/cupy_logo_1000px.png
   :width: 400

CuPy : NumPy & SciPy for GPU
============================

`CuPy <https://cupy.dev/>`_ is a NumPy/SciPy-compatible array library for GPU-accelerated computing with Python.

'''  # NOQA


# Long description of the sdist package in reST syntax.
SDIST_LONG_DESCRIPTION = _long_description_header + '''\
This package (``cupy``) is a source distribution.
For most users, use of pre-build wheel distributions are recommended:

- `cupy-cuda12x <https://pypi.org/project/cupy-cuda12x/>`_ (for CUDA 12.x)
- `cupy-cuda11x <https://pypi.org/project/cupy-cuda11x/>`_ (for CUDA 11.2 ~ 11.x)

- `cupy-rocm-5-0 <https://pypi.org/project/cupy-rocm-5-0/>`_ (for ROCm 5.0)
- `cupy-rocm-4-3 <https://pypi.org/project/cupy-rocm-4-3/>`_ (for ROCm 4.3)

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


class _WheelPythonConfig(TypedDict):
    pyenv: str
    python_tag: str
    abi_tag: str


# Key-value of python version to use for build and its
# corresponding configurations.
# Keys of the configuration are as follows:
# - `pyenv`: a full CPython version to use (only effective for Linux builds)
# - `python_tag`: a CPython implementation tag
# - `abi_tag`: a CPython ABI tag
WHEEL_PYTHON_VERSIONS: dict[str, _WheelPythonConfig] = {
    '3.9': {
        'pyenv': '3.9.0',
        'python_tag': 'cp39',
        'abi_tag': 'cp39',
    },
    '3.10': {
        'pyenv': '3.10.0',
        'python_tag': 'cp310',
        'abi_tag': 'cp310',
    },
    '3.11': {
        'pyenv': '3.11.0',
        'python_tag': 'cp311',
        'abi_tag': 'cp311',
    },
    '3.12': {
        'pyenv': '3.12.0',
        'python_tag': 'cp312',
        'abi_tag': 'cp312',
    },
    '3.13': {
        'pyenv': '3.13.2',
        'python_tag': 'cp313',
        'abi_tag': 'cp313',
    },
}
