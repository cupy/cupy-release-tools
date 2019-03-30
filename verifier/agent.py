#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
The agent code must be runnable on Python 2.6 (CentOS 6).
Additional dependency can be specified in Dockerfile.
"""

import argparse
import glob
import os
import shutil
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
            '-m', 'pip', 'install', '-vvv', '--user', args.dist,
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
