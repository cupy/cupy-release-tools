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
    SDIST_LONG_DESCRIPTION,
    WHEEL_LINUX_CONFIGS,
    WHEEL_WINDOWS_CONFIGS,
    WHEEL_PYTHON_VERSIONS,
    WHEEL_LONG_DESCRIPTION,
    VERIFY_PYTHON_VERSIONS,
    PYTHON_VERSIONS,
)  # NOQA

from dist_utils import (
    sdist_name,
    wheel_name,
    get_version_from_source_tree,
    get_system_cuda_version,
    find_file_in_path,
)  # NOQA


def log(msg):
    out = sys.stdout
    out.write('[{}]: {}\n'.format(time.asctime(), msg))
    out.flush()


def run_command(*cmd, **kwargs):
    log('Running command: {}'.format(str(cmd)))
    subprocess.check_call(cmd, **kwargs)


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
            '--target', choices=['sdist', 'wheel-linux', 'wheel-win'],
            required=True,
            help='build target')
        parser.add_argument(
            '--nccl-assets', type=str,
            help='path to the directory containing NCCL distributions')
        parser.add_argument(
            '--cuda', type=str,
            help='CUDA version for the wheel distribution')
        parser.add_argument(
            '--python', type=str, choices=PYTHON_VERSIONS, required=True,
            help='python version')

        # Build mode options:
        parser.add_argument(
            '--source', type=str,
            help='[build] path to the CuPy source tree; '
                 'must be a clean checkout')
        parser.add_argument(
            '--output', type=str, default='.',
            help='[build] path to the directory to place '
                 'the built distribution')

        # Verify mode options:
        parser.add_argument(
            '--dist', type=str,
            help='[verify] path to the CuPy distribution (sdist or wheel)')
        parser.add_argument(
            '--test', type=str, action='append', default=[],
            help='[verify] path to the directory containing CuPy unit tests '
                 '(can be specified for multiple times)')

        args = parser.parse_args()

        if args.action == 'build':
            assert args.source
            assert args.output
        elif args.action == 'verify':
            assert args.dist
            assert args.test

        return args

    def main(self):
        args = self.parse_args()

        if args.action == 'build':
            if args.target == 'wheel-win':
                self.build_windows(
                    args.target, args.nccl_assets, args.cuda, args.python,
                    args.source, args.output)
            else:
                self.build_linux(
                    args.target, args.nccl_assets, args.cuda, args.python,
                    args.source, args.output)
        elif args.action == 'verify':
            if args.target == 'wheel-win':
                self.verify_windows(
                    args.target, args.nccl_assets, args.cuda, args.python,
                    args.dist, args.test)
            else:
                self.verify_linux(
                    args.target, args.nccl_assets, args.cuda, args.python,
                    args.dist, args.test)

    def _create_builder_linux(self, image_tag, base_image, docker_ctx):
        """Create a docker image to build distributions."""

        python_versions = ' '.join(PYTHON_VERSIONS)
        log('Building Docker image: {}'.format(image_tag))
        run_command(
            'docker', 'build',
            '--tag', image_tag,
            '--build-arg', 'base_image={}'.format(base_image),
            '--build-arg', 'python_versions={}'.format(python_versions),
            '--build-arg', 'cython_version={}'.format(CYTHON_VERSION),
            docker_ctx,
        )

    def _create_verifier_linux(self, image_tag, base_image, docker_ctx):
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
        shutil.copy2(
            '{}/Dockerfile.{}'.format(docker_ctx, template),
            '{}/Dockerfile'.format(docker_ctx))

        python_versions = ' '.join(VERIFY_PYTHON_VERSIONS)
        log('Building Docker image: {}'.format(image_tag))
        run_command(
            'docker', 'build',
            '--tag', image_tag,
            '--build-arg', 'base_image={}'.format(base_image),
            '--build-arg', 'python_versions={}'.format(python_versions),
            docker_ctx,
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

        if nccl_assets is None:
            raise RuntimeError('NCCL assets must be specified for Linux')

        if target == 'wheel-linux':
            log(
                'Starting wheel-linux build from {} '
                '(version {}, for CUDA {} + Python {})'.format(
                    source, version, cuda_version, python_version))
            action = 'bdist_wheel'
            image_tag = 'cupy-builder-{}'.format(cuda_version)
            base_image = WHEEL_LINUX_CONFIGS[cuda_version]['image']
            package_name = WHEEL_LINUX_CONFIGS[cuda_version]['name']
            nccl_config = WHEEL_LINUX_CONFIGS[cuda_version]['nccl']
            long_description = WHEEL_LONG_DESCRIPTION.format(cuda=cuda_version)
            # Rename wheels to manylinux1.
            asset_name = wheel_name(
                package_name, version, python_version, 'linux_x86_64')
            asset_dest_name = wheel_name(
                package_name, version, python_version, 'manylinux1_x86_64')
        elif target == 'sdist':
            log('Starting sdist build from {} (version {})'.format(
                source, version))
            action = 'sdist'
            image_tag = 'cupy-builder-sdist'
            base_image = SDIST_CONFIG['image']
            package_name = 'cupy'
            nccl_config = SDIST_CONFIG['nccl']
            long_description = SDIST_LONG_DESCRIPTION
            asset_name = sdist_name('cupy', version)
            asset_dest_name = asset_name
            assert nccl_config is not None
        else:
            raise RuntimeError('unknown target')

        # Arguments for the agent.
        agent_args = [
            '--action', action,
            '--source', 'cupy',
            '--python', python_version,
            '--chown', '{}:{}'.format(os.getuid(), os.getgid()),
        ]

        # Add arguments to pass to setup.py.
        setup_args = [
            '--cupy-package-name', package_name,
            '--cupy-long-description', '../description.rst',
        ]
        if target == 'wheel-linux':
            # Add requirements for build.
            for req in WHEEL_PYTHON_VERSIONS[python_version]['requires']:
                agent_args += ['--requires', req]

            setup_args += [
                '--cupy-no-rpath',
            ]
            for lib in WHEEL_LINUX_CONFIGS[cuda_version]['libs']:
                setup_args += ['--cupy-wheel-lib', lib]
            agent_args += setup_args

        # Create a working directory.
        workdir = tempfile.mkdtemp(prefix='cupy-dist-')

        try:
            log('Using working directory: {}'.format(workdir))

            # Copy source tree to working directory.
            log('Copying source tree from: {}'.format(source))
            shutil.copytree(source, '{}/cupy'.format(workdir))

            # Add long description file.
            if long_description is not None:
                with open('{}/description.rst'.format(workdir), 'w') as f:
                    f.write(long_description)

            # Copy builder directory to working directory.
            docker_ctx = '{}/builder'.format(workdir)
            log('Copying builder directory to: '.format(docker_ctx))
            shutil.copytree('builder/', docker_ctx)

            # Extract NCCL archive.
            log('Creating nccl directory under builder directory')
            nccl_workdir = '{}/nccl'.format(docker_ctx)
            os.mkdir(nccl_workdir)
            if nccl_config:
                log('Extracting NCCL archive')
                extract_nccl_archive(nccl_config, nccl_assets, nccl_workdir)
            else:
                log('NCCL is not installed for this build')

            # Creates a Docker image to build distribution.
            self._create_builder_linux(image_tag, base_image, docker_ctx)

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

    def _check_windows_environment(self, cuda_version, python_version):
        # Check if this script is running on Windows.
        if not sys.platform.startswith('win32'):
            raise RuntimeError(
                'you are on non-Windows system: {}'.format(sys.platform))

        # Check Python version.
        current_python_version = '.'.join(map(str, sys.version_info[0:3]))
        if python_version != current_python_version:
            log('Note: Building wheel for Python {} using Python {}'.format(
                python_version, current_python_version))

        # Check CUDA runtime version.
        config = WHEEL_WINDOWS_CONFIGS[cuda_version]
        cuda_check_version = config['check_version']
        current_cuda_version = get_system_cuda_version(config['cudart_lib'])
        if current_cuda_version is None:
            raise RuntimeError(
                'Cannot build wheel without CUDA Runtime installed')
        elif not cuda_check_version(current_cuda_version):
            raise RuntimeError(
                'Cannot build wheel for CUDA {} using CUDA {}'.format(
                    cuda_version, current_cuda_version))

    def build_windows(
            self, target, nccl_assets, cuda_version, python_version,
            source, output):
        """Build a single wheel distribution for Windows.

        Note that Windows build is not isolated.
        """

        # Perform additional check as Windows environment is not isoalted.
        self._check_windows_environment(cuda_version, python_version)

        if target != 'wheel-win':
            raise ValueError('unknown target')

        if nccl_assets is not None:
            raise RuntimeError('NCCL not supported on Windows')

        version = get_version_from_source_tree(source)

        log(
            'Starting wheel-win build from {} '
            '(version {}, for CUDA {} + Python {})'.format(
                source, version, cuda_version, python_version))

        action = 'bdist_wheel'
        package_name = WHEEL_WINDOWS_CONFIGS[cuda_version]['name']
        long_description = WHEEL_LONG_DESCRIPTION.format(cuda=cuda_version)
        asset_name = wheel_name(
            package_name, version, python_version, 'win_amd64')
        asset_dest_name = asset_name

        agent_args = [
            '--action', action,
            '--source', 'cupy',
        ]

        # Add requirements for build.
        for req in WHEEL_PYTHON_VERSIONS[python_version]['requires']:
            agent_args += ['--requires', req]

        # Add arguments to pass to setup.py.
        setup_args = [
            '--cupy-package-name', package_name,
            '--cupy-long-description', '../description.rst',
        ]
        for lib in WHEEL_WINDOWS_CONFIGS[cuda_version]['libs']:
            libpath = find_file_in_path(lib)
            if libpath is None:
                raise RuntimeError(
                    'Library {} could not be found in PATH'.format(lib))
            setup_args += ['--cupy-wheel-lib', libpath]
        agent_args += setup_args

        # Create a working directory.
        workdir = tempfile.mkdtemp(prefix='cupy-dist-')

        try:
            log('Using working directory: {}'.format(workdir))

            # Copy source tree and NCCL to working directory.
            log('Copying source tree from: {}'.format(source))
            shutil.copytree(source, '{}/cupy'.format(workdir))

            # Add long description file.
            if long_description is not None:
                with open('{}/description.rst'.format(workdir), 'w') as f:
                    f.write(long_description)

            # Build.
            log('Starting build')
            run_command(
                sys.executable, '{}/builder/agent.py'.format(os.getcwd()),
                *agent_args, cwd=workdir)
            log('Finished build')

            # Copy assets.
            asset_path = '{}/cupy/dist/{}'.format(workdir, asset_name)
            output_path = '{}/{}'.format(output, asset_dest_name)
            log('Copying asset from {} to {}'.format(asset_path, output_path))
            shutil.copy2(asset_path, output_path)

        finally:
            log('Removing working directory: {}'.format(workdir))
            try:
                shutil.rmtree(workdir)
            except OSError as e:
                # TODO(kmaehashi): On Windows, removal of `.git` directory may
                # fail with PermissionError (on Python 3) or OSError (on
                # Python 2). Note that PermissionError inherits OSError.
                log('Failed to clean-up working directory: {}\n\n'
                    'Please remove the working directory manually: {}'.format(
                        e, workdir))

    def verify_linux(
            self, target, nccl_assets, cuda_version, python_version,
            dist, tests):
        """Verify a single distribution for Linux."""

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
            log('Starting verification for {} on {} with Python {}'.format(
                dist, image, python_version))
            self._verify_linux(
                image_tag_system, image, dist, tests,
                python_version, nccl_assets, nccl_config)

    def _verify_linux(
            self, image_tag, base_image, dist, tests, python_version,
            nccl_assets, nccl_config):
        dist_basename = os.path.basename(dist)

        # Arguments for the agent.
        agent_args = [
            '--python', python_version,
            '--dist', dist_basename,
            '--chown', '{}:{}'.format(os.getuid(), os.getgid()),
        ]

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

            # Copy verifier directory to working directory.
            docker_ctx = '{}/verifier'.format(workdir)
            log('Copying verifier directory to: '.format(docker_ctx))
            shutil.copytree('verifier/', docker_ctx)

            # Extract NCCL archive.
            log('Creating nccl directory under verifier directory')
            nccl_workdir = '{}/nccl'.format(docker_ctx)
            os.mkdir(nccl_workdir)
            if nccl_config:
                log('Extracting NCCL archive')
                extract_nccl_archive(nccl_config, nccl_assets, nccl_workdir)
            else:
                log('NCCL is not installed for this verification')

            # Creates a Docker image to verify specified distribution.
            self._create_verifier_linux(image_tag, base_image, docker_ctx)

            # Verify.
            log('Starting verification')
            self._run_container(image_tag, workdir, agent_args)
            log('Finished verification')

        finally:
            log('Removing working directory: {}'.format(workdir))
            shutil.rmtree(workdir)

    def verify_windows(
            self, target, nccl_assets, cuda_version, python_version,
            dist, tests):
        """Verify a single distribution for Windows."""

        # Perform additional check as Windows environment is not isoalted.
        self._check_windows_environment(cuda_version, python_version)

        if target != 'wheel-win':
            raise ValueError('unknown target')

        if nccl_assets is not None:
            raise RuntimeError('NCCL not supported on Windows')

        log('Starting verification for {} with Python {}'.format(
            dist, python_version))

        dist_basename = os.path.basename(dist)

        # Arguments for the agent.
        agent_args = [
            '--dist', dist,
        ]

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

            # Verify.
            log('Starting verification')
            run_command(
                sys.executable, '{}/verifier/agent.py'.format(os.getcwd()),
                *agent_args, cwd=workdir)
            log('Finished verification')

        finally:
            log('Removing working directory: {}'.format(workdir))
            shutil.rmtree(workdir)


if __name__ == '__main__':
    Controller().main()
