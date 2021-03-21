#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This tool copies the directory tree created by the library installer
(`cupyx.tools.install_library`) to $CUDA_PATH.
"""

import argparse
import os
import pathlib
import shutil
import sys


def merge_directory(src_dir, dst_dir):
    """Merge two directory trees."""
    for srcpath, _, files in os.walk(src_dir):
        srcpath = pathlib.Path(srcpath)
        destpath = dst_dir / srcpath.relative_to(src_dir)
        if not destpath.exists():
            print('Creating directory: {}'.format(destpath))
            destpath.mkdir()
        for f in files:
            srcfile = srcpath / f
            destfile = destpath / f
            print('Copying: {} <- {}'.format(destfile, srcfile))
            shutil.copy2(srcfile, destfile)


def _child(path):
    """Returns a child of the given path."""
    children = list(path.iterdir())
    assert len(children) == 1
    return children[0]


def _install_library(name, src_dir, dst_dir, *, install_map):
    src_dir = pathlib.Path(src_dir)
    dst_dir = pathlib.Path(dst_dir)

    # $src_dir/$CUDA_VERSION/$name/$LIB_VERSION/$libdir_src
    src_dir = _child(src_dir)  # $CUDA_VERSION
    src_dir = src_dir.joinpath(name)  # $name
    src_dir = _child(src_dir)  # $LIB_VERSION

    for (s, d) in install_map.items():
        merge_directory(src_dir / s, dst_dir / d)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--src', type=str, required=True)
    parser.add_argument('--dst', type=str, required=True)
    args = parser.parse_args()

    src_dir = args.src
    dst_dir = args.dst

    if sys.platform == 'linux':
        _install_library(
            'cutensor', src_dir, dst_dir, {
                'lib': 'lib64',
                'include': 'include',
            })
        _install_library(
            'nccl', src_dir, dst_dir, {
                'lib': 'lib64',
                'include': 'include',
            })
        _install_library(
            'cudnn', src_dir, dst_dir, {
                'lib64': 'lib64',
                'include': 'include',
            })
    elif sys.platform == 'win32':
        _install_library(
            'cutensor', src_dir, dst_dir, {
                'lib': 'bin',
                'include': 'include',
            })
        _install_library(
            'cudnn', src_dir, dst_dir, {
                'bin': 'bin',
                'lib': 'lib',
                'include': 'include',
            })
    else:
        assert False


if __name__ == '__main__':
    main()
