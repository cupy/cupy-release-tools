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
        dstpath = dst_dir / srcpath.relative_to(src_dir)
        if not dstpath.exists():
            print('Creating directory: {}'.format(dstpath))
            dstpath.mkdir()
        for f in files:
            srcfile = srcpath / f
            dstfile = dstpath / f
            print('Copying: {} <- {}'.format(dstfile, srcfile))
            shutil.copy2(srcfile, dstfile)


def _child(path):
    """Returns a child of the given path."""
    children = list(path.iterdir())
    if len(children) == 0:
        return None
    assert len(children) == 1
    return children[0]


def _install_library(name, src_dir, dst_dir, install_map):
    src_dir = pathlib.Path(src_dir)
    dst_dir = pathlib.Path(dst_dir)

    # $src_dir/$CUDA_VERSION/$name/$LIB_VERSION
    src_dir = _child(src_dir)  # $CUDA_VERSION
    if src_dir is None:
        print('Skip installing {} (no preloading libraries)'.format(name))
        return
    src_dir = src_dir.joinpath(name)  # $name
    if not src_dir.exists():
        print('Skip installing {} (unavailable)'.format(name))
        return
    src_dir = _child(src_dir)  # $LIB_VERSION

    for child in src_dir.iterdir():
        dst_name = install_map.get(child.name, child.name)
        if child.is_dir():
            merge_directory(child, dst_dir / dst_name)
        else:
            dstfile = dst_dir / dst_name
            print('Copying: {} <- {}'.format(dstfile, child))
            shutil.copy2(child, dstfile)


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
                'lib': 'lib',  # static libs
                'include': 'include',
            })
    else:
        assert False


if __name__ == '__main__':
    main()
