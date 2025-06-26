#!/usr/bin/env python
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time


class _VerifierAgentArgs(argparse.Namespace):
    dist: str | None
    python: str | None
    cuda: str | None
    preload: list[str]
    chown: str | None


class VerifierAgent:

    @staticmethod
    def _log(msg: str) -> None:
        print(f'[VerifierAgent] [{time.asctime()}]: {msg}', flush=True)

    def _run(self, *cmd: str) -> None:
        self._log(f'Running command: {cmd}')
        env = dict(os.environ)
        env['CUPY_DEBUG_LIBRARY_LOAD'] = '1'
        subprocess.check_call(cmd, env=env)

    @staticmethod
    def parse_args() -> tuple[_VerifierAgentArgs, list[str]]:
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '--dist', type=str,
            help='Path to the distribution (sdist or wheel)')
        parser.add_argument(
            '--python', type=str,
            help='Python version to use for setup')
        parser.add_argument(
            '--cuda', type=str,
            help='CUDA version')
        parser.add_argument(
            '--preload', action='append', type=str, default=[],
            help='Install the library and preload')
        parser.add_argument(
            '--chown', type=str,
            help='Reset owner of files to the specified `uid:gid`')

        return parser.parse_known_args(namespace=_VerifierAgentArgs())

    def main(self) -> None:
        args, pytest_args = self.parse_args()

        pycommand = [sys.executable]
        if args.python:
            os.environ['PYENV_VERSION'] = args.python
            self._log(f'Using Python {args.python}')
            pycommand = ['pyenv', 'exec', 'python']
        else:
            self._log('Using Python from system')

        assert args.dist is not None

        self._log('Installing distribution...')
        cmdline = [
            *pycommand,
            '-m',
            'pip',
            'install',
            '-v',
            '--user',
            args.dist,
        ]
        self._run(*cmdline)

        self._log('Installing CUDA Runtime headers (if necessary)...')
        verifier_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
        cmdline = [*pycommand, f'{verifier_dir}/setup_cuda_runtime_headers.py']
        self._run(*cmdline)

        # Importing CuPy should not be emit warnings,
        # Raise on warning to to catch bugs of preload warnings, e.g.:
        # https://github.com/cupy/cupy/pull/4933
        self._log('CuPy Configuration (before preloading)')
        cmdline = [
            *pycommand,
            '-Werror',
            '-c',
            'import cupy; cupy.show_config()',
        ]
        self._run(*cmdline)

        for p in args.preload:
            assert args.cuda is not None
            self._log(f'Installing preload libraries ({p})...')
            cmdline = [
                *pycommand,
                '-m',
                'cupyx.tools.install_library',
                '--library',
                p,
                '--cuda',
                args.cuda,
            ]
            self._run(*cmdline)

        self._log('CuPy Configuration (after preloading)')
        cmdline = [
            *pycommand,
            '-Werror',
            '-c',
            'import cupy; import cupy.cuda.cudnn; cupy.show_config()',
        ]
        self._run(*cmdline)

        try:
            cmdline = [*pycommand, '-m', 'pytest', *pytest_args]
            self._run(*cmdline)
        finally:
            if args.chown:
                self._log('Resetting owner/group of the source tree...')
                self._run('chown', '-R', args.chown, '.')


if __name__ == '__main__':
    VerifierAgent().main()
