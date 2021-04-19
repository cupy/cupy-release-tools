#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os
import subprocess
import sys
import time


class VerifierAgent(object):

    def _log(self, msg):
        out = sys.stdout
        out.write('[VerifierAgent] [{0}]: {1}\n'.format(time.asctime(), msg))
        out.flush()

    def _run(self, *cmd):
        self._log('Running command: {0}'.format(str(cmd)))
        subprocess.check_call(cmd)

    def parse_args(self):
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

        return parser.parse_known_args()

    def main(self):
        args, pytest_args = self.parse_args()

        pycommand = [sys.executable]
        if args.python:
            os.environ['PYENV_VERSION'] = args.python
            self._log('Using Python {0}'.format(args.python))
            pycommand = ['pyenv', 'exec', 'python']
        else:
            self._log('Using Python from system')

        self._log('Installing distribution...')
        cmdline = pycommand + [
            '-m', 'pip', 'install', '-v', '--user', args.dist,
        ]
        self._run(*cmdline)

        # Importing CuPy should not be emit warnings,
        # Raise on warning to to catch bugs of preload warnings, e.g.:
        # https://github.com/cupy/cupy/pull/4933
        cmdline = pycommand + [
            '-Werror', '-c', 'import cupy; cupy.show_config()'
        ]
        self._run(*cmdline)

        for p in args.preload:
            self._log('Installing preload libraries ({})...'.format(p))
            cmdline = pycommand + [
                '-m', 'cupyx.tools.install_library',
                '--library', p, '--cuda', args.cuda,
            ]
            self._run(*cmdline)

        try:
            cmdline = pycommand + ['-m', 'pytest'] + pytest_args
            self._run(*cmdline)
        finally:
            if args.chown:
                self._log('Resetting owner/group of the source tree...')
                self._run('chown', '-R', args.chown, '.')


if __name__ == '__main__':
    VerifierAgent().main()
