#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse

from dist_config import (
    WHEEL_LINUX_CONFIGS,
    WHEEL_PYTHON_VERSIONS,
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
            '--target', choices=['sdist', 'wheel-linux'], required=True,
            help='build target')
        parser.add_argument(
            '--source', type=str, required=True,
            help='path to the CuPy source tree; must be a clean checkout')

        # Options specific for wheels:
        parser.add_argument(
            '--cuda', type=str,
            help='CUDA version for the wheel distribution')
        parser.add_argument(
            '--python', type=str, choices=sorted(WHEEL_PYTHON_VERSIONS.keys()),
            help='python version to build wheel with')

        return parser.parse_args()

    def main(self):
        args = self.parse_args()
        version = get_version_from_source_tree(args.source)
        if args.target == 'wheel-linux':
            print('DIST_FILE_NAME="{}"'.format(
                wheel_name(
                    args.cuda, version, args.python, 'manylinux1_x86_64'),
            ))
            print('DIST_PACKAGE_NAME="{}"'.format(
                WHEEL_LINUX_CONFIGS[args.cuda]['name'],
            ))
        elif args.target == 'sdist':
            print('DIST_FILE_NAME="{}"'.format(
                sdist_name('cupy', version)
            ))
            print('DIST_PACKAGE_NAME="cupy"')


if __name__ == '__main__':
    DistInfoPrinter().main()
