#!/usr/bin/env python

import argparse
import itertools
import os
import subprocess
import sys

import distlib.locators


CP39 = 'cp39-cp39'
CP310 = 'cp310-cp310'
CP311 = 'cp311-cp311'
CP312 = 'cp312-cp312'
CP313 = 'cp313-cp313'
LINUX = 'manylinux2014_x86_64'
LINUX_V11 = 'manylinux1_x86_64'
LINUX_AARCH64 = 'manylinux2014_aarch64'
WINDOWS = 'win_amd64'


sdist_project = 'cupy'

_main_cuda_x86_matrix = list(itertools.product(
    (CP310, CP311, CP312, CP313), (LINUX, WINDOWS)))
_main_cuda_aarch64_matrix = list(itertools.product(
    (CP310, CP311, CP312, CP313), (LINUX_AARCH64,)))
_main_rocm_matrix = list(itertools.product(
    (CP310, CP311, CP312, CP313), (LINUX,)))
_v13_cuda_x86_matrix = list(itertools.product(
    (CP39, CP310, CP311, CP312, CP313), (LINUX, WINDOWS)))
_v13_cuda_aarch64_matrix = list(itertools.product(
    (CP39, CP310, CP311, CP312, CP313), (LINUX_AARCH64,)))
_v13_rocm_matrix = list(itertools.product(
    (CP39, CP310, CP311, CP312, CP313), (LINUX,)))

pypi_wheel_projects = {
    # v14.x
    '14': [
        ('cupy-cuda11x',  _main_cuda_x86_matrix + _main_cuda_aarch64_matrix),
        ('cupy-cuda12x',  _main_cuda_x86_matrix + _main_cuda_aarch64_matrix),
        # ('cupy-rocm-6-2', _main_rocm_matrix),
    ],

    # v13.x
    '13': [
        ('cupy-cuda11x',  _v13_cuda_x86_matrix + _v13_cuda_aarch64_matrix),
        ('cupy-cuda12x',  _v13_cuda_x86_matrix + _v13_cuda_aarch64_matrix),
        # ('cupy-rocm-4-3', _v13_rocm_matrix),
        # ('cupy-rocm-5-0', _v13_rocm_matrix),
        # ('cupy-rocm-6-2', _v13_rocm_matrix),
    ],
}

github_wheel_projects = pypi_wheel_projects


def get_basenames(project, version):
    # List all wheels including unsupported ones by the current Python
    distlib.locators.is_compatible = lambda *args: True
    locator = distlib.locators.SimpleScrapingLocator(
        'https://pypi.org/simple/')
    proj = locator.get_project(project)['urls']
    if version not in proj:
        return []
    return [os.path.basename(url) for url in proj[version]]


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


def verify(project, expected, actual) -> bool:
    print('🔵 Project: {}'.format(project))
    expected = set(expected)
    actual = set(actual)
    error = False
    for project in sorted(expected - actual):
        error = True
        print('  ❓ Missing: {}'.format(project))
    for project in sorted(actual - expected):
        error = True
        print('  ⚠️  Unexpected: {}'.format(project))
    for project in sorted(actual & expected):
        print('  👀 Found: {}'.format(project))
    if error:
        print('  ❌ Check Fail')
    else:
        print('  ✅ Check Pass')
    print()
    return not error


def get_expected_wheels(wheel_projects, version):
    branch = str(version.split('.')[0])
    return {
        project: [
            get_expected_wheel_basename(project, version, cpython, arch)
            for (cpython, arch) in matrix
        ]
        for (project, matrix) in wheel_projects[branch]
    }


def parse_args(argv) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', required=True)
    parser.add_argument('--github', action='store_true', default=False)
    parser.add_argument('--pypi-sdist', action='store_true', default=False)
    parser.add_argument('--pypi-wheel', action='store_true', default=False)
    return parser.parse_args(argv[1:])


def main(argv):
    options = parse_args(argv)

    version = options.version
    if version.startswith('v'):
        version = version[1:]
    branch = str(version.split('.')[0])

    success = True

    # Verify assets on GitHub release
    if options.github:
        expected = (
            list(itertools.chain(*get_expected_wheels(
                github_wheel_projects, version).values())) +
            [get_expected_sdist_basename(sdist_project, version)])
        success = verify(
            'GitHub Release',
            expected,
            get_basenames_github(version)) and success

    if options.pypi_sdist:
        expected = [get_expected_sdist_basename(sdist_project, version)]
        actual = get_basenames(sdist_project, version)
        success = verify(sdist_project, expected, actual) and success

    if options.pypi_wheel:
        expected = get_expected_wheels(pypi_wheel_projects, version)
        for project, _ in pypi_wheel_projects[branch]:
            actual = get_basenames(project, version)
            success = verify(project, expected[project], actual) and success

    if not success:
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
