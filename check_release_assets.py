#!/usr/bin/env python

import itertools
import os
import subprocess
import sys

import distlib.locators


CP36 = 'cp36-cp36m'
CP37 = 'cp37-cp37m'
CP38 = 'cp38-cp38'
CP39 = 'cp39-cp39'
CP310 = 'cp310-cp310'
LINUX = 'manylinux1_x86_64'
LINUX_AARCH64 = 'manylinux2014_aarch64'
WINDOWS = 'win_amd64'


sdist_project = 'cupy'

_v11_cuda_matrix = list(itertools.product(
    (CP37, CP38, CP39, CP310), (LINUX, WINDOWS)))
_v11_rocm_matrix = list(itertools.product(
    (CP37, CP38, CP39, CP310), (LINUX,)))
_v10_cuda_matrix = list(itertools.product(
    (CP37, CP38, CP39, CP310), (LINUX, WINDOWS)))
_v10_rocm_matrix = list(itertools.product(
    (CP37, CP38, CP39, CP310), (LINUX,)))

wheel_projects = {
    # v11.x
    '11': [
        ('cupy-cuda102',  _v11_cuda_matrix + [
            (CP37, LINUX_AARCH64),
            (CP38, LINUX_AARCH64),
            (CP39, LINUX_AARCH64),
            (CP310, LINUX_AARCH64),
        ]),
        ('cupy-cuda110',  _v11_cuda_matrix),
        ('cupy-cuda111',  _v11_cuda_matrix),
        ('cupy-cuda112',  _v11_cuda_matrix),
        ('cupy-cuda113',  _v11_cuda_matrix),
        ('cupy-cuda114',  _v11_cuda_matrix),
        ('cupy-cuda115',  _v11_cuda_matrix),
        ('cupy-cuda116',  _v11_cuda_matrix),
        ('cupy-rocm-4-2', _v11_rocm_matrix),
        ('cupy-rocm-4-3', _v11_rocm_matrix),
        ('cupy-rocm-5-0', _v11_rocm_matrix),
    ],

    # v10.x
    '10': [
        ('cupy-cuda102',  _v10_cuda_matrix + [
            (CP37, LINUX_AARCH64),
            (CP38, LINUX_AARCH64),
            (CP39, LINUX_AARCH64),
            (CP310, LINUX_AARCH64),
        ]),
        ('cupy-cuda110',  _v10_cuda_matrix),
        ('cupy-cuda111',  _v10_cuda_matrix),
        ('cupy-cuda112',  _v10_cuda_matrix),
        ('cupy-cuda113',  _v10_cuda_matrix),
        ('cupy-cuda114',  _v10_cuda_matrix),
        ('cupy-cuda115',  _v10_cuda_matrix),
        ('cupy-cuda116',  _v10_cuda_matrix),
        ('cupy-rocm-4-0', _v10_rocm_matrix),
        ('cupy-rocm-4-2', _v10_rocm_matrix),
        ('cupy-rocm-4-3', _v10_rocm_matrix),
        ('cupy-rocm-5-0', _v10_rocm_matrix),
    ],
}


def get_basenames(project, version):
    locator = distlib.locators.PyPIJSONLocator('https://pypi.org/pypi')
    proj = locator.get_project(project)
    if version not in proj:
        return []
    return [os.path.basename(url) for url in proj[version].download_urls]


def get_basenames_github(version):
    return subprocess.check_output([
        'gh', 'release', '--repo', 'cupy/cupy',
        'view', f'v{version}',
        '--json', 'assets',
        '--jq', '.assets[].name']).decode().splitlines()


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
    expected = {}
    for (project, matrix) in wheel_projects[branch]:
        expected[project] = [
            get_expected_wheel_basename(project, version, cpython, arch)
            for (cpython, arch) in matrix
        ]

    if any([x in version for x in ('a', 'b', 'rc')]):
        # Pre-release, verify assets on GitHub release
        verify(
            'GitHub Release',
            itertools.chain(*expected.values()),
            get_basenames_github(version))
    else:
        # Stable release, find from PyPI
        for project, _ in wheel_projects[branch]:
            actual = get_basenames(project, version)
            verify(project, expected[project], actual)

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
