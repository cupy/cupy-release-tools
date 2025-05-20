#!/usr/bin/env python
"""
This tool copies the directory tree created by the library installer
(`cupyx.tools.install_library`) to $CUDA_PATH.
"""
from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping


def merge_directory(src_dir: Path, dst_dir: Path) -> None:
    """Merge two directory trees."""
    # MEMO: Path.walk is only available from py3.12
    for srcpath, files in (
        (Path(srcpath), files) for srcpath, _, files in os.walk(src_dir)
    ):
        dstpath = dst_dir / srcpath.relative_to(src_dir)
        if not dstpath.exists():
            print(f'Creating directory: {dstpath}')
            dstpath.mkdir()
        for f in files:
            srcfile = srcpath / f
            dstfile = dstpath / f
            print(f'Copying: {dstfile} <- {srcfile}')
            shutil.copy2(srcfile, dstfile)


def _child(path: Path) -> Path | None:
    """Returns a child of the given path."""
    children = list(path.iterdir())
    if len(children) == 0:
        return None
    assert len(children) == 1
    return children[0]


def _install_library(
    name: str,
    src_dir: Path,
    dst_dir: Path,
    install_map: Mapping[str, str],
) -> None:
    # $src_dir/$CUDA_VERSION/$name/$LIB_VERSION
    src_dir_ = _child(src_dir)  # $CUDA_VERSION
    if src_dir_ is None:
        print(f'Skip installing {name} (no preloading libraries)')
        return
    src_dir_ = src_dir_.joinpath(name)  # $name
    if not src_dir_.exists():
        print(f'Skip installing {name} (unavailable)')
        return
    src_dir_ = _child(src_dir_)  # $LIB_VERSION
    assert src_dir_ is not None

    for child in src_dir_.iterdir():
        dst_name = install_map.get(child.name, child.name)
        if child.is_dir():
            merge_directory(child, dst_dir / dst_name)
        else:
            dstfile = dst_dir / dst_name
            print(f'Copying: {dstfile} <- {child}')
            shutil.copy2(child, dstfile)


class _OptLibArgs(argparse.Namespace):
    src: str
    dst: str


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--src', type=str, required=True)
    parser.add_argument('--dst', type=str, required=True)
    args = parser.parse_args(namespace=_OptLibArgs())

    src_dir = Path(args.src)
    dst_dir = Path(args.dst)

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
        raise AssertionError(f'Unsupported platform: {sys.platform}.')


if __name__ == '__main__':
    main()
