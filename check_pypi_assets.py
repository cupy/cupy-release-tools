#!/usr/bin/env python

import itertools
import os
import sys

import distlib.locators


CP35 = 'cp35-cp35m'
CP36 = 'cp36-cp36m'
CP37 = 'cp37-cp37m'
CP38 = 'cp38-cp38'
CP39 = 'cp39-cp39'
LINUX = 'manylinux1_x86_64'
WINDOWS = 'win_amd64'


sdist_project = 'cupy'

_v9_cuda_matrix = list(itertools.product(
    (CP36, CP37, CP38, CP39), (LINUX, WINDOWS)))
_v8_cuda_matrix = [(CP35, LINUX)] + _v9_cuda_matrix
wheel_projects = {
    # v8.x
    '8': [
        ('cupy-cuda90',   _v8_cuda_matrix),
        ('cupy-cuda92',   _v8_cuda_matrix),
        ('cupy-cuda100',  _v8_cuda_matrix),
        ('cupy-cuda101',  _v8_cuda_matrix),
        ('cupy-cuda102',  _v8_cuda_matrix),
        ('cupy-cuda110',  _v8_cuda_matrix),
        ('cupy-cuda111',  _v8_cuda_matrix),
        ('cupy-cuda112',  _v8_cuda_matrix),
    ],

    # v9.x
    '9': [
        ('cupy-cuda92',    _v9_cuda_matrix),
        ('cupy-cuda100',   _v9_cuda_matrix),
        ('cupy-cuda101',   _v9_cuda_matrix),
        ('cupy-cuda102',   _v9_cuda_matrix),
        ('cupy-cuda110',   _v9_cuda_matrix),
        ('cupy-cuda111',   _v9_cuda_matrix),
        ('cupy-cuda112',   _v9_cuda_matrix),
        ('cupy-rocm-4-0',  list(itertools.product(
            (CP36, CP37, CP38, CP39), (LINUX,)))),
    ],
}


def get_basenames(project, version):
    locator = distlib.locators.PyPIJSONLocator('https://pypi.org/pypi')
    proj = locator.get_project(project)
    if version not in proj:
        return []
    return [os.path.basename(url) for url in proj[version].download_urls]


def get_expected_sdist_basename(project, version):
    return '{project}-{version}.tar.gz'.format(
        project=project,
        version=version,
    )


def get_expected_wheel_basename(project, version, abi, arch):
    return '{project}-{version}-{abi}-{arch}.whl'.format(
        project=project.replace('-', '_'),
        version=version,
        abi=abi,
        arch=arch,
    )


def verify(project, expected, actual):
    print('🔵 Project: {}'.format(project))
    expected = set(expected)
    actual = set(actual)
    error = False
    for project in (expected - actual):
        error = True
        print('  ❓ Missing: {}'.format(project))
    for project in (actual - expected):
        error = True
        print('  ⚠️  Unexpected: {}'.format(project))
    for project in (actual & expected):
        print('  👀 Found: {}'.format(project))
    if error:
        print('  ❌ Check Fail')
    else:
        print('  ✅ Check Pass')
    print()


def main(argv):
    if len(argv) != 2:
        print(f'Usage: {argv[0]} VERSION')
        return 1

    version = argv[1]
    branch = str(version.split('.')[0])

    # sdist
    expected = [get_expected_sdist_basename(sdist_project, version)]
    actual = get_basenames(sdist_project, version)
    verify(sdist_project, expected, actual)

    # wheel
    for (project, matrix) in wheel_projects[branch]:
        expected = [
            get_expected_wheel_basename(project, version, cpython, arch)
            for (cpython, arch) in matrix
        ]
        actual = get_basenames(project, version)
        verify(project, expected, actual)

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
