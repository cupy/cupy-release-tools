# -*- coding: utf-8 -*-

import ctypes
import ctypes.util
import imp
import os

from dist_config import (
    WHEEL_PYTHON_VERSIONS,
)  # NOQA


def sdist_name(package_name, version):
    return '{package_name}-{version}.tar.gz'.format(
        package_name=package_name,
        version=version,
    )


def wheel_name(pkg_name, version, python_version, platform_tag):
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


def get_version_from_source_tree(source_tree):
    version_file_path = '{}/cupy/_version.py'.format(source_tree)
    return imp.load_source('_version', version_file_path).__version__


def get_system_cuda_version(cudart_name='cudart'):
    filename = ctypes.util.find_library(cudart_name)
    if filename is None:
        return None
    libcudart = ctypes.CDLL(filename)
    version = ctypes.c_int()
    assert libcudart.cudaRuntimeGetVersion(ctypes.byref(version)) == 0
    return version.value


def find_file_in_path(executable, path=None):
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
    else:
        return executable
