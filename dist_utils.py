from __future__ import annotations

import ctypes
import ctypes.util
import os

from dist_config import WHEEL_PYTHON_VERSIONS


def wheel_linux_platform_tag(cpu: str, manylinux: bool) -> str:
    assert cpu in {'aarch64', 'x86_64'}
    tag = 'manylinux2014' if manylinux else 'linux'
    return f'{tag}_{cpu}'


def sdist_name(package_name: str, version: str) -> str:
    return f'{package_name}-{version}.tar.gz'


def wheel_name(
    pkg_name: str, version: str, python_version: str, platform_tag: str
) -> str:
    # https://www.python.org/dev/peps/pep-0491/#file-name-convention
    return (
        '{distribution}-{version}-{python_tag}-{abi_tag}-'
        '{platform_tag}.whl').format(
            distribution=pkg_name.replace('-', '_'),
            version=version,
            python_tag=WHEEL_PYTHON_VERSIONS[python_version]['python_tag'],
            abi_tag=WHEEL_PYTHON_VERSIONS[python_version]['abi_tag'],
            platform_tag=platform_tag,
    )


def get_system_cuda_version(cudart_name: str = 'cudart') -> int | None:
    filename = ctypes.util.find_library(cudart_name)
    if filename is None:
        return None
    libcudart = ctypes.CDLL(filename)
    version = ctypes.c_int()
    assert libcudart.cudaRuntimeGetVersion(ctypes.byref(version)) == 0
    return version.value


def find_file_in_path(executable: str, path: str | None = None) -> str | None:
    """Tries to find `executable` in the directories listed in `path`.

    A string listing directories separated by 'os.pathsep'; defaults to
    `os.environ['PATH']`.  Returns the complete filename or None if not found.
    """
    if path is None:
        path = os.environ['PATH']

    paths = path.split(os.pathsep)
    if not os.path.isfile(executable):
        for p in paths:
            f = os.path.join(p, executable)
            if os.path.isfile(f):
                return f
        return None
    return executable
