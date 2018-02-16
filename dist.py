#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os
import random
import shutil
import string
import subprocess
import sys
import tempfile
import time


from dist_config import (
    CYTHON_VERSION,
    SDIST_CONFIG,
    WHEEL_LINUX_CONFIGS,
    WHEEL_PYTHON_VERSIONS,
    VERIFY_PYTHON_VERSIONS,
)  # NOQA

from dist_utils import (
    sdist_name,
    wheel_name,
    get_version_from_source_tree,
)  # NOQA


def log(msg):
    out = sys.stdout
    out.write('[{}]: {}\n'.format(time.asctime(), msg))
    out.flush()


def run_command(*cmd):
    log('Running command: {}'.format(str(cmd)))
    subprocess.check_call(cmd)


def make_random_name(length=10):
    return ''.join(
        random.choice(string.ascii_lowercase + string.digits)
        for i in range(length))


def extract_nccl_archive(nccl_config, nccl_assets, dest_dir):
    log('Extracting NCCL assets from {} to {}'.format(nccl_assets, dest_dir))
    asset_type = nccl_config['type']
    if asset_type == 'v1-deb':
        for nccl_deb in nccl_config['files']:
            run_command(
                'dpkg', '-x',
                '{}/{}'.format(nccl_assets, nccl_deb),
                dest_dir,
            )
        # Adjust paths to align with tarball.
        shutil.move(
            '{}/usr/lib/x86_64-linux-gnu'.format(dest_dir),
            '{}/lib'.format(dest_dir)
        )
        shutil.move(
            '{}/usr/include'.format(dest_dir),
            '{}/include'.format(dest_dir)
        )
    elif asset_type == 'v2-tar':
        for nccl_tar in nccl_config['files']:
            run_command(
                'tar', '-x',
                '-f', '{}/{}'.format(nccl_assets, nccl_tar),
                '-C', dest_dir, '--strip', '1',
            )
    else:
        raise RuntimeError('unknown NCCL asset type: {}'.format(asset_type))


class Controller(object):

    def parse_args(self):
        parser = argparse.ArgumentParser()

        parser.add_argument(
            '--action', choices=['build', 'verify'], required=True,
            help='action to perform')

        # Common options:
        parser.add_argument(
            '--target', choices=['sdist', 'wheel-linux'], required=True,
            help='build target')
        parser.add_argument(
            '--nccl-assets', type=str,
            help='path to the directory containing NCCL distributions')
        parser.add_argument(
            '--cuda', type=str,
            help='CUDA version for the wheel distribution')
        parser.add_argument(
            '--python', type=str, required=True,
            choices=sorted(WHEEL_PYTHON_VERSIONS.keys()),
            help='python version')

        # Build mode options:
        parser.add_argument(
            '--source', type=str,
            help='path to the CuPy source tree; must be a clean checkout')
        parser.add_argument(
            '--output', type=str, default='.',
            help='path to the directory to place the built distribution')

        # Verify mode options:
        parser.add_argument(
            '--dist', type=str,
            help='path to the CuPy distribution (sdist or wheel)')
        parser.add_argument(
            '--test', type=str, action='append', default=[],
            help='path to the directory containing CuPy unit tests '
                 '(can be specified for multiple times)')

        args = parser.parse_args()

        if args.action == 'build':
            assert args.nccl_assets
            assert args.source
            assert args.output
        elif args.action == 'verify':
            assert args.dist
            assert args.test

        return args

    def main(self):
        args = self.parse_args()

        if args.action == 'build':
            self.build_linux(
                args.target, args.nccl_assets, args.cuda, args.python,
                args.source, args.output)
        elif args.action == 'verify':
            self.verify_linux(
                args.target, args.nccl_assets, args.cuda, args.python,
                args.dist, args.test)

    def _create_builder_linux(self, image_tag, base_image):
        """Create a docker image to build distributions."""

        log('Building Docker image: {}'.format(image_tag))
        run_command(
            'docker', 'build',
            '--tag', image_tag,
            '--build-arg', 'base_image={}'.format(base_image),
            '--build-arg', 'cython_version={}'.format(CYTHON_VERSION),
            'builder-linux',
        )

    def _create_verifier_linux(self, image_tag, base_image):
        """Create a docker image to verify distributions."""

        # Choose Dockerfile template
        if 'rhel' in base_image or 'centos' in base_image:
            log('Using RHEL Dockerfile template')
            template = 'rhel'
        elif 'ubuntu' in base_image:
            log('Using Debian Dockerfile template')
            template = 'debian'
        else:
            raise RuntimeError(
                'cannot detect OS from image name: '.format(base_image))

        python_versions = ' '.join(sorted(VERIFY_PYTHON_VERSIONS.values()))
        log('Building Docker image: {}'.format(image_tag))
        run_command(
            'docker', 'build',
            '--tag', image_tag,
            '--build-arg', 'base_image={}'.format(base_image),
            '--build-arg', 'python_versions={}'.format(python_versions),
            '--file', 'verifier-linux/Dockerfile.{}'.format(template),
            'verifier-linux',
        )

    def _run_container(self, image_tag, workdir, agent_args):
        log('Running docker container with image: {}'.format(image_tag))
        run_command(
            'nvidia-docker', 'run',
            '--rm',
            '--volume', '{}:/work'.format(workdir),
            '--workdir', '/work',
            image_tag,
            *agent_args
        )

    def build_linux(
            self, target, nccl_assets, cuda_version, python_version,
            source, output):
        """Build a single wheel distribution for Linux."""

        version = get_version_from_source_tree(source)

        if target == 'wheel-linux':
            log(
                'Starting wheel-linux build from {} '
                '(version {}, for CUDA {} + Python {})'.format(
                    source, version, cuda_version, python_version))
            action = 'bdist_wheel'
            # Rename wheels to manylinux1.
            asset_name = wheel_name(
                cuda_version, version, python_version, 'linux_x86_64')
            asset_dest_name = wheel_name(
                cuda_version, version, python_version, 'manylinux1_x86_64')
            image_tag = 'cupy-builder-{}'.format(cuda_version)
            base_image = WHEEL_LINUX_CONFIGS[cuda_version]['image']
            package_name = WHEEL_LINUX_CONFIGS[cuda_version]['name']
            nccl_config = WHEEL_LINUX_CONFIGS[cuda_version]['nccl']
        elif target == 'sdist':
            log('Starting sdist build from {} (version {})'.format(
                source, version))
            action = 'sdist'
            asset_name = sdist_name('cupy', version)
            asset_dest_name = asset_name
            image_tag = 'cupy-builder-sdist'
            base_image = SDIST_CONFIG['image']
            nccl_config = SDIST_CONFIG['nccl']
            assert nccl_config is not None
        else:
            raise RuntimeError('unknown target')

        # Creates a Docker image to build distribution.
        self._create_builder_linux(image_tag, base_image)

        # Arguments for the agent.
        agent_args = [
            '--action', action,
            '--source', 'cupy',
            '--python-tag', '{}-{}'.format(
                python_version,
                WHEEL_PYTHON_VERSIONS[python_version]['linux_abi_tag']),
            '--chown', '{}:{}'.format(os.getuid(), os.getgid()),
        ]
        if nccl_config:
            agent_args += ['--nccl', 'nccl']

        if target == 'wheel-linux':
            # Add requirements for build.
            for req in WHEEL_PYTHON_VERSIONS[python_version]['requires']:
                agent_args += ['--requires', req]

            # Add arguments to pass to setup.py.
            setup_args = ['--cupy-package-name', package_name]
            for lib in WHEEL_LINUX_CONFIGS[cuda_version]['libs']:
                setup_args += ['--cupy-wheel-lib', lib]
            agent_args += setup_args

        # Create a working directory.
        workdir = tempfile.mkdtemp(prefix='cupy-dist-')

        try:
            log('Using working directory: {}'.format(workdir))

            # Copy source tree and NCCL to working directory.
            log('Copying source tree from: {}'.format(source))
            shutil.copytree(source, '{}/cupy'.format(workdir))

            # Extract NCCL.
            if nccl_config:
                nccl_workdir = '{}/nccl'.format(workdir)
                os.mkdir(nccl_workdir)
                extract_nccl_archive(nccl_config, nccl_assets, nccl_workdir)
            else:
                log('NCCL is not used for this package')

            # Build.
            log('Starting build')
            self._run_container(image_tag, workdir, agent_args)
            log('Finished build')

            # Copy assets.
            asset_path = '{}/cupy/dist/{}'.format(workdir, asset_name)
            output_path = '{}/{}'.format(output, asset_dest_name)
            log('Copying asset from {} to {}'.format(asset_path, output_path))
            shutil.copy2(asset_path, output_path)

        finally:
            log('Removing working directory: {}'.format(workdir))
            shutil.rmtree(workdir)

    def verify_linux(
            self, target, nccl_assets, cuda_version, python_version,
            dist, tests):
        """Verify a single distribution for Linux."""

        # Creates a Docker image to verify specified distribution.
        if target == 'sdist':
            image_tag = 'cupy-verifier-sdist'
            base_image = SDIST_CONFIG['verify_image']
            systems = SDIST_CONFIG['verify_systems']
            nccl_config = SDIST_CONFIG['nccl']
            assert cuda_version is None
        elif target == 'wheel-linux':
            image_tag = 'cupy-verifier-wheel-linux-{}'.format(cuda_version)
            base_image = WHEEL_LINUX_CONFIGS[cuda_version]['verify_image']
            systems = WHEEL_LINUX_CONFIGS[cuda_version]['verify_systems']
            nccl_config = None
        else:
            raise RuntimeError('unknown target')

        for system in systems:
            image = base_image.format(system=system)
            image_tag_system = '{}-{}'.format(image_tag, system)
            pyenv_python_version = VERIFY_PYTHON_VERSIONS[python_version]
            log('Starting verification for {} on {} '
                'with Python {} ({})'.format(
                    dist, image, python_version, pyenv_python_version))
            self._verify_linux(
                image_tag_system, image, dist, tests,
                pyenv_python_version, nccl_assets, nccl_config)

    def _verify_linux(
            self, image_tag, base_image, dist, tests, python_version,
            nccl_assets, nccl_config):
        dist_basename = os.path.basename(dist)

        self._create_verifier_linux(image_tag, base_image)

        # Arguments for the agent.
        agent_args = [
            '--python', python_version,
            '--dist', dist_basename,
            '--chown', '{}:{}'.format(os.getuid(), os.getgid()),
        ]
        if nccl_config:
            agent_args += ['--nccl', 'nccl']

        # Add arguments for `python -m pytest`.
        agent_args += ['tests']

        # Create a working directory.
        workdir = tempfile.mkdtemp(prefix='cupy-dist-')

        try:
            log('Using working directory: {}'.format(workdir))

            # Copy dist and tests to working directory.
            log('Copying distribution from: {}'.format(dist))
            shutil.copy2(dist, '{}/{}'.format(workdir, dist_basename))
            tests_dir = '{}/tests'.format(workdir)
            os.mkdir(tests_dir)
            for test in tests:
                log('Copying tests from: {}'.format(test))
                shutil.copytree(
                    test,
                    '{}/{}'.format(tests_dir, os.path.basename(test)))

            # Extract NCCL.
            if nccl_config:
                nccl_workdir = '{}/nccl'.format(workdir)
                os.mkdir(nccl_workdir)
                extract_nccl_archive(nccl_config, nccl_assets, nccl_workdir)
            else:
                log('NCCL is not installed for verification')

            # Verify.
            log('Starting verification')
            self._run_container(image_tag, workdir, agent_args)
            log('Finished verification')

        finally:
            log('Removing working directory: {}'.format(workdir))
            shutil.rmtree(workdir)


if __name__ == '__main__':
    Controller().main()
