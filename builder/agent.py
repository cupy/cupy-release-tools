#!/usr/bin/env python

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time


class _BuilderAgentArgs(argparse.Namespace):
    action: str
    source: str
    python: str | None
    requires: list[str]
    chown: str | None


class BuilderAgent:

    @staticmethod
    def _log(msg: str) -> None:
        print(f'[BuilderAgent] [{time.asctime()}]: {msg}', flush=True)

    def _run(self, *cmd: str) -> None:
        self._log(f'Running command: {cmd}')
        subprocess.check_call(cmd)

    @staticmethod
    def parse_args() -> tuple[_BuilderAgentArgs, list[str]]:
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '--action', type=str, required=True,
            help='setup.py action to invoke')
        parser.add_argument(
            '--source', type=str, required=True,
            help='Path to the CuPy source directory')
        parser.add_argument(
            '--python', type=str,
            help='Python version to use for setup')
        parser.add_argument(
            '--requires', action='append', type=str, default=[],
            help='Python requirements to install prior to setup')
        parser.add_argument(
            '--chown', type=str,
            help='Reset owner of files to the specified `uid:gid`')

        return parser.parse_known_args(namespace=_BuilderAgentArgs())

    def main(self) -> None:
        args, setup_args = self.parse_args()

        pycommand = [sys.executable]
        if args.python:
            os.environ['PYENV_VERSION'] = args.python
            self._log(f'Using Python {args.python}')
            pycommand = ['pyenv', 'exec', 'python']
        else:
            self._log('Using Python from system')

        if 0 < len(args.requires):
            self._log('Installing python libraries...')
            cmdline = [*pycommand, '-m', 'pip', 'install', *args.requires]
            self._run(*cmdline)

        self._log('Changing directory to cupy source tree')
        os.chdir(args.source)
        try:
            self._log('Running CuPy setup...')
            cmdline = [*pycommand, 'setup.py', args.action, *setup_args]
            if sys.platform.startswith('linux'):
                cmdline = ['/build-wrapper', *cmdline]
            self._run(*cmdline)
        finally:
            if args.chown:
                self._log('Resetting owner/group of the source tree...')
                self._run('chown', '-R', args.chown, '.')


if __name__ == '__main__':
    BuilderAgent().main()
