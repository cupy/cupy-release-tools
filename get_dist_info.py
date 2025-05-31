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
    sdist_name,
    wheel_linux_platform_tag,
    wheel_name,
)  # NOQA


class _DistInfoArgs(argparse.Namespace):
    target: Literal['sdist', 'wheel-linux', 'wheel-win']
    source: str
    version: str
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
        parser.add_argument(
            '--version', type=str, required=True,
            help='version of the package')

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
        if args.target == 'wheel-linux':
            pkg_name = WHEEL_LINUX_CONFIGS[args.cuda]['name']
            arch = WHEEL_LINUX_CONFIGS[args.cuda].get('arch', 'x86_64')
            filename = wheel_name(
                pkg_name, args.version, args.python,
                wheel_linux_platform_tag(arch, True))
        elif args.target == 'wheel-win':
            pkg_name = WHEEL_WINDOWS_CONFIGS[args.cuda]['name']
            filename = wheel_name(pkg_name, args.version, args.python, 'win_amd64')
        elif args.target == 'sdist':
            pkg_name = 'cupy'
            filename = sdist_name(pkg_name, args.version)
        else:
            raise AssertionError('Unreachable')
        print(f'DIST_FILE_NAME="{filename}"')
        print(f'DIST_PACKAGE_NAME="{pkg_name}"')


if __name__ == '__main__':
    DistInfoPrinter().main()
