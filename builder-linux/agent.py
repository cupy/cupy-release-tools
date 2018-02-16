#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
            '--python-tag', type=str,
            help='Python implementation tag to use for build')
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

        if args.python_tag:
            os.environ['PATH'] = '/opt/python/{0}/bin:{1}'.format(
                args.python_tag, os.environ['PATH'])
            self._log('Using Python Tag {0}'.format(args.python_tag))

        if 0 < len(args.requires):
            self._log('Installing python libraries...')
            self._run('pip', 'install', *args.requires)

        self._log('Changing directory to cupy source tree')
        os.chdir(args.source)
        try:
            self._log('Running CuPy setup...')
            self._run(
                'python', 'setup.py', args.action, *setup_args)
        finally:
            if args.chown:
                self._log('Resetting owner/group of the source tree...')
                self._run('chown', '-R', args.chown, '.')


if __name__ == '__main__':
    BuilderAgent().main()
