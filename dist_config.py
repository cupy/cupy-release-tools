from __future__ import annotations

from typing import TYPE_CHECKING, Literal, TypedDict

if TYPE_CHECKING:
    from collections.abc import Callable

    # Can be imported from typing for >= 3.11
    from typing_extensions import NotRequired


# CuPy major version supported by this tool.
CUPY_MAJOR_VERSION = '14'


class _SDistConfig(TypedDict):
    image: str
    verify_image: str
    verify_systems: list[str]


# Key-value of sdist build settings.
# See descriptions of WHEEL_LINUX_CONFIGS for details.
SDIST_CONFIG: _SDistConfig = {
    'image': 'nvidia/cuda:12.0.1-devel-rockylinux8',
    # This image contains NCCL.
    'verify_image': 'nvidia/cuda:12.0.1-devel-{system}',
    'verify_systems': ['ubuntu22.04'],
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
    preloads_cuda_version: NotRequired[str]
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
# - `preloads_cuda_version`: CUDA version used to install optional CUDA
#                            libraries (optional, default: dict key)
# - `verify_image`: a name of the base docker image name used for verify
# - `verify_systems`: a list of systems to verify on; expaneded as {system} in
#                     `verify_image`.
# - `system_packages`: a string of depending library names expanded into the
#                      package manager command.
WHEEL_LINUX_CONFIGS: dict[str, _WheelLinuxConfig] = {
    '12.x': {
        # CUDA Enhanced Compatibility wheel (for CUDA 12.x)
        'name': 'cupy-cuda12x',
        'kind': 'cuda',
        'platform_version': '12.x',
        # Use the latest CUDA version for build.
        'image': 'cupy/cupy-release-tools:cuda-runfile-12.9.0-el8-amd64',
        'libs': [],
        'includes': [],
        'preloads': ['cutensor', 'nccl'],
        'verify_image': 'nvidia/cuda:{system}',
        'verify_systems': [
            # Test on all supported CUDA version variants.
            '12.0.1-runtime-ubuntu20.04',
            '12.1.1-runtime-ubuntu22.04',
            '12.2.0-runtime-ubuntu22.04',
            '12.3.0-runtime-ubuntu22.04',
            '12.4.0-runtime-ubuntu22.04',
            '12.5.0-runtime-ubuntu22.04',
            '12.6.0-runtime-ubuntu22.04',
            '12.8.0-runtime-ubuntu22.04',
            '12.9.0-runtime-ubuntu22.04',
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
        'image': 'cupy/cupy-release-tools:cuda-runfile-12.9.0-el8-aarch64',
        'libs': [],
        'includes': [],
        'preloads': ['nccl'],
        'preloads_cuda_version': '12.x',
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
            '12.9.0-runtime-ubi8',
        ],
        'system_packages': '',
    },
    '13.x': {
        # CUDA Enhanced Compatibility wheel (for CUDA 13.x)
        'name': 'cupy-cuda13x',
        'kind': 'cuda',
        'platform_version': '13.x',
        # Use the latest CUDA version for build.
        # Note: oldest RHEL supported in CUDA 13 is v8
        'image': 'cupy/cupy-release-tools:cuda-runfile-13.0.0-el8-amd64',
        'libs': [],
        'includes': [],
        'preloads': ['cutensor', 'nccl'],
        'verify_image': 'nvidia/cuda:{system}',
        'verify_systems': [
            # Test on all supported CUDA version variants.
            '13.0.0-runtime-ubuntu22.04',
        ],
        'system_packages': '',
    },
    '13.x-aarch64': {
        # CUDA Enhanced Compatibility wheel (for CUDA 13.x)
        'name': 'cupy-cuda13x',
        'kind': 'cuda',
        'arch': 'aarch64',
        'platform_version': '13.x',
        # Use the latest image.
        'image': 'cupy/cupy-release-tools:cuda-runfile-13.0.0-el8-aarch64',
        'libs': [],
        'includes': [],
        'preloads': ['nccl'],
        'preloads_cuda_version': '13.x',
        'verify_image': 'nvidia/cuda:{system}',
        'verify_systems': [
            # Test on all supported CUDA version variants.
            '13.0.0-runtime-ubi8',
        ],
        'system_packages': '',
    },
    'rocm-7.0': {
        'name': 'cupy-rocm-7-0',
        'kind': 'rocm',
        'platform_version': '7.0',
        'image': 'rocm/dev-almalinux-8:7.0-complete',
        'libs': [],
        'includes': [],
        'preloads': [],
        'verify_image': 'rocm/dev-ubuntu-24.04:7.0.2',
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
    '12.x': {
        # CUDA Enhanced Compatibility wheel (for CUDA 12.x)
        'name': 'cupy-cuda12x',
        'kind': 'cuda',
        'libs': [],
        'preloads': ['cutensor'],
        'cudart_lib': 'cudart64_12',  # binary compatible between CUDA 12.x
        'check_version': lambda x: 12090 <= x < 12100,  # CUDA 12.9
    },
    '13.x': {
        # CUDA Enhanced Compatibility wheel (for CUDA 13.x)
        'name': 'cupy-cuda13x',
        'kind': 'cuda',
        'libs': [],
        'preloads': ['cutensor'],
        'cudart_lib': 'cudart64_13',  # binary compatible between CUDA 13.x
        'check_version': lambda x: 13000 <= x < 13010,  # CUDA 13.0
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

- `cupy-cuda13x <https://pypi.org/project/cupy-cuda13x/>`_ (for NVIDIA CUDA 13.x)
- `cupy-cuda12x <https://pypi.org/project/cupy-cuda12x/>`_ (for NVIDIA CUDA 12.x)

- `cupy-rocm-7-0 <https://pypi.org/project/cupy-rocm-7-0/>`_ (for AMD ROCm 7.0)

Please see `Installation Guide <https://docs.cupy.dev/en/latest/install.html>`_ for the detailed instructions.
'''  # NOQA


# Long description of the CUDA wheel package in reST syntax.
# `{version}` and `{wheel_suffix}` will be replaced by the CUDA version (e.g., `9.0`).
WHEEL_LONG_DESCRIPTION_CUDA = _long_description_header + '''\
This is a CuPy wheel (precompiled binary) package for CUDA {version}.
You need to install `CUDA Toolkit {version} <https://developer.nvidia.com/cuda-toolkit-archive>`_ locally to use these packages.
Alternatively, you can install this package together with all needed CUDA components from PyPI by passing the ``[ctk]`` tag::

   $ pip install cupy-cuda{wheel_suffix}[ctk]

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
    '3.14': {
        'pyenv': '3.14.2',
        'python_tag': 'cp314',
        'abi_tag': 'cp314',
    },
}
