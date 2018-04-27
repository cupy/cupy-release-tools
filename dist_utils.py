# -*- coding: utf-8 -*-

import ctypes
import ctypes.util
import imp

from dist_config import (
    WHEEL_LINUX_CONFIGS,
    WHEEL_PYTHON_VERSIONS,
)  # NOQA


def sdist_name(package_name, version):
    return '{package_name}-{version}.tar.gz'.format(
        package_name=package_name,
        version=version,
    )


def wheel_name(cuda, version, python_version, platform_tag):
    # https://www.python.org/dev/peps/pep-0491/#file-name-convention
    if platform_tag.startswith('linux'):
        abi_key = 'abi_tag_linux'
    elif platform_tag.startswith('win'):
        abi_key = 'abi_tag_win'
    else:
        raise RuntimeError('unsupported platform')

    return (
        '{distribution}-{version}-{python_tag}-{abi_tag}-'
        '{platform_tag}.whl').format(
            distribution=WHEEL_LINUX_CONFIGS[cuda]['name'].replace('-', '_'),
            version=version,
            python_tag=WHEEL_PYTHON_VERSIONS[python_version]['python_tag'],
            abi_tag=WHEEL_PYTHON_VERSIONS[python_version][abi_key],
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
