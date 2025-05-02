#!/usr/bin/env python3
from __future__ import annotations

import argparse
from typing import Literal

from dist_config import (
    WHEEL_LINUX_CONFIGS,
    WHEEL_PYTHON_VERSIONS,
    WHEEL_WINDOWS_CONFIGS,
)  # NOQA
from dist_utils import (
    get_version_from_source_tree,
    sdist_name,
    wheel_linux_platform_tag,
    wheel_name,
)  # NOQA


class _DistInfoArgs(argparse.Namespace):
    target: Literal['sdist', 'wheel-linux', 'wheel-win']
    source: str
    cuda: str
    python: str


class DistInfoPrinter:

    @staticmethod
    def parse_args() -> _DistInfoArgs:
        parser = argparse.ArgumentParser()

        parser.add_argument(
            '--target', required=True,
            choices=['sdist', 'wheel-linux', 'wheel-win'],
            help='build target')
        parser.add_argument(
            '--source', type=str, required=True,
            help='path to the CuPy source tree; must be a clean checkout')

        # Options specific for wheels:
        parser.add_argument(
            '--cuda', type=str,
            help='CUDA version for the wheel distribution')
        parser.add_argument(
            '--python', type=str, choices=WHEEL_PYTHON_VERSIONS.keys(),
            help='python version to build wheel with')

        return parser.parse_args(namespace=_DistInfoArgs())

    def main(self) -> None:
        args = self.parse_args()
        version = get_version_from_source_tree(args.source)
        if args.target == 'wheel-linux':
            pkg_name = WHEEL_LINUX_CONFIGS[args.cuda]['name']
            arch = WHEEL_LINUX_CONFIGS[args.cuda].get('arch', 'x86_64')
            filename = wheel_name(
                pkg_name, version, args.python,
                wheel_linux_platform_tag(arch, True))
        elif args.target == 'wheel-win':
            pkg_name = WHEEL_WINDOWS_CONFIGS[args.cuda]['name']
            filename = wheel_name(pkg_name, version, args.python, 'win_amd64')
        elif args.target == 'sdist':
            pkg_name = 'cupy'
            filename = sdist_name(pkg_name, version)
        else:
            raise AssertionError('Unreachable')
        print(f'DIST_FILE_NAME="{filename}"')
        print(f'DIST_PACKAGE_NAME="{pkg_name}"')


if __name__ == '__main__':
    DistInfoPrinter().main()
