#!/usr/bin/env python
from __future__ import annotations

import argparse
import itertools
import os
import subprocess
import sys
from typing import TYPE_CHECKING

import distlib.locators

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping, Sequence

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

_MatrixType = list[tuple[str, str]]

_main_cuda_x86_matrix: _MatrixType = list(itertools.product(
    (CP310, CP311, CP312, CP313), (LINUX, WINDOWS)))
_main_cuda_aarch64_matrix: _MatrixType = list(itertools.product(
    (CP310, CP311, CP312, CP313), (LINUX_AARCH64,)))
_main_rocm_matrix: _MatrixType = list(itertools.product(
    (CP310, CP311, CP312, CP313), (LINUX,)))
_v13_cuda_x86_matrix: _MatrixType = list(itertools.product(
    (CP39, CP310, CP311, CP312, CP313), (LINUX, WINDOWS)))
_v13_cuda_aarch64_matrix: _MatrixType = list(itertools.product(
    (CP39, CP310, CP311, CP312, CP313), (LINUX_AARCH64,)))
_v13_rocm_matrix: _MatrixType = list(itertools.product(
    (CP39, CP310, CP311, CP312, CP313), (LINUX,)))

pypi_wheel_projects = {
    # v14.x
    '14': [
        ('cupy-cuda11x', _main_cuda_x86_matrix + _main_cuda_aarch64_matrix),
        ('cupy-cuda12x', _main_cuda_x86_matrix + _main_cuda_aarch64_matrix),
        # ('cupy-rocm-6-2', _main_rocm_matrix),
    ],

    # v13.x
    '13': [
        ('cupy-cuda11x', _v13_cuda_x86_matrix + _v13_cuda_aarch64_matrix),
        ('cupy-cuda12x', _v13_cuda_x86_matrix + _v13_cuda_aarch64_matrix),
        # ('cupy-rocm-4-3', _v13_rocm_matrix),
        # ('cupy-rocm-5-0', _v13_rocm_matrix),
        # ('cupy-rocm-6-2', _v13_rocm_matrix),
    ],
}

github_wheel_projects = pypi_wheel_projects


def get_basenames(project: str, version: str) -> list[str]:
    # List all wheels including unsupported ones by the current Python
    distlib.locators.is_compatible = lambda *_: True
    locator = distlib.locators.SimpleScrapingLocator(
        'https://pypi.org/simple/')
    proj: dict[str, str] = locator.get_project(project)['urls']
    if version not in proj:
        return []
    return [os.path.basename(url) for url in proj[version]]


def get_basenames_github(version: str) -> list[str]:
    return subprocess.check_output([
        'gh', 'release', '--repo', 'cupy/cupy',
        'view', f'v{version}',
        '--json', 'assets',
        '--jq', '.assets[].name'], encoding='UTF-8').splitlines()


def get_expected_sdist_basename(project: str, version: str) -> str:
    return f'{project}-{version}.tar.gz'


def get_expected_wheel_basename(
    project: str, version: str, abi: str, arch: str
) -> str:
    project = project.replace('-', '_')
    return f'{project}-{version}-{abi}-{arch}.whl'


def verify(
    project: str, expected: Iterable[str], actual: Iterable[str]
) -> bool:
    print(f'🔵 Project: {project}')
    expected = set(expected)
    actual = set(actual)
    error = False
    for p in sorted(expected - actual):
        error = True
        print(f'  ❓ Missing: {p}')
    for p in sorted(actual - expected):
        error = True
        print(f'  ⚠️  Unexpected: {p}')
    for p in sorted(actual & expected):
        print(f'  👀 Found: {p}')
    if error:
        print('  ❌ Check Fail')
    else:
        print('  ✅ Check Pass')
    print()
    return not error


def get_expected_wheels(
    wheel_projects: Mapping[str, list[tuple[str, _MatrixType]]], version: str
) -> dict[str, list[str]]:
    branch = str(version.split('.')[0])
    return {
        project: [
            get_expected_wheel_basename(project, version, cpython, arch)
            for (cpython, arch) in matrix
        ]
        for (project, matrix) in wheel_projects[branch]
    }


class _LibAssetsArgs(argparse.Namespace):
    version: str
    github: bool
    pypi_sdist: bool
    pypi_wheel: bool


def parse_args(argv: Sequence[str]) -> _LibAssetsArgs:
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', required=True)
    parser.add_argument('--github', action='store_true', default=False)
    parser.add_argument('--pypi-sdist', action='store_true', default=False)
    parser.add_argument('--pypi-wheel', action='store_true', default=False)
    return parser.parse_args(argv[1:], namespace=_LibAssetsArgs())


def main(argv: Sequence[str]) -> int:
    options = parse_args(argv)

    version = options.version
    version = version.removeprefix('v')
    branch = str(version.split('.')[0])

    success = True

    # Verify assets on GitHub release
    if options.github:
        expected_gh = [
            *itertools.chain.from_iterable(
                get_expected_wheels(github_wheel_projects, version).values()
            ),
            get_expected_sdist_basename(sdist_project, version),
        ]
        success = verify(
            'GitHub Release',
            expected_gh,
            get_basenames_github(version)) and success

    if options.pypi_sdist:
        expected_sdist = [get_expected_sdist_basename(sdist_project, version)]
        actual = get_basenames(sdist_project, version)
        success = verify(sdist_project, expected_sdist, actual) and success

    if options.pypi_wheel:
        expected_whl = get_expected_wheels(pypi_wheel_projects, version)
        for project, _ in pypi_wheel_projects[branch]:
            actual = get_basenames(project, version)
            success = verify(
                project, expected_whl[project], actual) and success

    if not success:
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
