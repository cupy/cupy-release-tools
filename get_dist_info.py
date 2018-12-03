#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse

from dist_config import (
    WHEEL_LINUX_CONFIGS,
    WHEEL_WINDOWS_CONFIGS,
    PYTHON_VERSIONS,
)  # NOQA

from dist_utils import (
    sdist_name,
    wheel_name,
    get_version_from_source_tree,
)  # NOQA


class DistInfoPrinter(object):

    def parse_args(self):
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
            '--python', type=str, choices=PYTHON_VERSIONS,
            help='python version to build wheel with')

        return parser.parse_args()

    def main(self):
        args = self.parse_args()
        version = get_version_from_source_tree(args.source)
        if args.target == 'wheel-linux':
            pkg_name = WHEEL_LINUX_CONFIGS[args.cuda]['name']
            filename = wheel_name(
                pkg_name, version, args.python, 'manylinux1_x86_64')
        elif args.target == 'wheel-win':
            pkg_name = WHEEL_WINDOWS_CONFIGS[args.cuda]['name']
            filename = wheel_name(pkg_name, version, args.python, 'win_amd64')
        elif args.target == 'sdist':
            pkg_name = 'cupy'
            filename = sdist_name(pkg_name, version)
        print('DIST_FILE_NAME="{}"'.format(filename))
        print('DIST_PACKAGE_NAME="{}"'.format(pkg_name))


if __name__ == '__main__':
    DistInfoPrinter().main()
