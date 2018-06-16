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


class BuilderAgent(object):

    def _log(self, msg):
        out = sys.stdout
        out.write('[BuilderAgent] [{0}]: {1}\n'.format(time.asctime(), msg))
        out.flush()

    def _run(self, *cmd):
        self._log('Running command: {0}'.format(str(cmd)))
        subprocess.check_call(cmd)

    def parse_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '--action', type=str, required=True,
            help='setup.py action to invoke')
        parser.add_argument(
            '--source', type=str, required=True,
            help='Path to the CuPy source directory')
        parser.add_argument(
            '--nccl', type=str,
            help='Path to the extracted NCCL binary distribution directory')
        parser.add_argument(
            '--python', type=str,
            help='Python version to use for setup')
        parser.add_argument(
            '--requires', action='append', type=str, default=[],
            help='Python requirements to install prior to setup')
        parser.add_argument(
            '--chown', type=str,
            help='Reset owner of files to the specified `uid:gid`')

        return parser.parse_known_args()

    def main(self):
        args, setup_args = self.parse_args()

        if args.nccl:
            self._log('Installing NCCL...')
            for f in glob.glob('{0}/lib/lib*'.format(args.nccl)):
                shutil.copy(f, '/usr/local/cuda/lib64')
            for f in glob.glob('{0}/include/*.h'.format(args.nccl)):
                shutil.copy(f, '/usr/local/cuda/include')
        else:
            self._log('Skip NCCL installation')

        pycommand = [sys.executable]
        if args.python:
            os.environ['PYENV_VERSION'] = args.python
            self._log('Using Python {0}'.format(args.python))
            pycommand = ['pyenv', 'exec', 'python']
        else:
            self._log('Using Python from system')

        if 0 < len(args.requires):
            self._log('Installing python libraries...')
            cmdline = pycommand + ['-m', 'pip', 'install'] + args.requires
            self._run(*cmdline)

        self._log('Changing directory to cupy source tree')
        os.chdir(args.source)
        try:
            self._log('Running CuPy setup...')
            cmdline = pycommand + ['setup.py', args.action] + setup_args
            self._run(*cmdline)
        finally:
            if args.chown:
                self._log('Resetting owner/group of the source tree...')
                self._run('chown', '-R', args.chown, '.')


if __name__ == '__main__':
    BuilderAgent().main()
