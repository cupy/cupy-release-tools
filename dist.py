#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import time


from dist_config import (
    CUPY_MAJOR_VERSION,
    CYTHON_VERSION,
    FASTRLOCK_VERSION,
    SDIST_CONFIG,
    SDIST_LONG_DESCRIPTION,
    WHEEL_LINUX_CONFIGS,
    WHEEL_WINDOWS_CONFIGS,
    WHEEL_PYTHON_VERSIONS,
    WHEEL_LONG_DESCRIPTION_CUDA,
    WHEEL_LONG_DESCRIPTION_ROCM,
)  # NOQA

from dist_utils import (
    wheel_linux_platform_tag,
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


def run_command(*cmd, extra_env=None, **kwargs):
    env = None
    if extra_env is not None:
        env = os.environ.copy()
        env.update(extra_env)
    log('Running command: {}'.format(str(cmd)))
    subprocess.check_call(cmd, env=env, **kwargs)


def run_command_output(*cmd, **kwargs):
    log('Running command: {}'.format(str(cmd)))
    return subprocess.check_output(cmd, **kwargs)


def prepare_cuda_opt_library(library, cuda_version, prefix):
    """Extracts the library to the prefix, and returns preloading metadata."""

    target_system = platform.system()
    log('Retrieving preloading metadata for {} / CUDA {} / {}'.format(
        library, cuda_version, target_system))
    command = [
        sys.executable,
        'cupy/cupyx/tools/install_library.py',
        '--library', library,
        '--cuda', cuda_version,
        '--prefix', prefix,
    ]
    records = json.loads(
        run_command_output(*command, '--action', 'dump').decode('utf-8'))
    for record in records:
        if record['cuda'] == cuda_version:
            metadata = {
                'version': record[library],
                'filenames': record['assets'][target_system]['filenames'],
            }
            break
    else:
        raise RuntimeError('Combination not supported by install_library tool')

    log('Extracting the library to {}'.format(prefix))
    run_command(*command, '--action', 'install')

    return metadata


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
            '--cuda', type=str,
            help='CUDA version for the wheel distribution')
        parser.add_argument(
            '--python', type=str, choices=WHEEL_PYTHON_VERSIONS.keys(),
            required=True,
            help='python version')
        parser.add_argument(
            '--dry-run', action='store_true', default=False,
            help='only generate builder/verifier Docker images - Linux only')
        parser.add_argument(
            '--push', action='store_true', default=False,
            help='push builder/verifier Docker images - Linux only')
        parser.add_argument(
            '--rmi', action='store_true', default=False,
            help='remove builder/verifier Docker images after build '
                 '- Linux only')

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
                    args.target, args.cuda, args.python,
                    args.source, args.output)
            else:
                self.build_linux(
                    args.target, args.cuda, args.python,
                    args.source, args.output, args.dry_run, args.push,
                    args.rmi)
        elif args.action == 'verify':
            if args.target == 'wheel-win':
                self.verify_windows(
                    args.target, args.cuda, args.python,
                    args.dist, args.test)
            else:
                self.verify_linux(
                    args.target, args.cuda, args.python,
                    args.dist, args.test, args.dry_run, args.push, args.rmi)

    def _create_builder_linux(
            self, image_tag, base_image, builder_dockerfile, system_packages,
            docker_ctx, push):
        """Create a docker image to build distributions."""

        python_versions = ' '.join(
            [x['pyenv'] for x in WHEEL_PYTHON_VERSIONS.values()])
        log('Building Docker image: {}'.format(image_tag))
        run_command(
            'docker', 'build',
            '--file', f'{docker_ctx}/{builder_dockerfile}',
            '--tag', image_tag,
            '--cache-from', image_tag,
            '--build-arg', 'BUILDKIT_INLINE_CACHE=1',
            '--build-arg', 'base_image={}'.format(base_image),
            '--build-arg', 'python_versions={}'.format(python_versions),
            '--build-arg', 'cython_version={}'.format(CYTHON_VERSION),
            '--build-arg', 'fastrlock_version={}'.format(FASTRLOCK_VERSION),
            '--build-arg', 'system_packages={}'.format(system_packages),
            docker_ctx,
            extra_env={'DOCKER_BUILDKIT': '1'},
        )
        if push:
            run_command('docker', 'push', image_tag)

    def _create_verifier_linux(
            self, image_tag, base_image, system_packages, docker_ctx, push):
        """Create a docker image to verify distributions."""

        # Choose Dockerfile template
        # TODO(kmaehashi): make this dist_config option
        if 'ubi8' in base_image:
            log('Using EL8 Dockerfile template')
            template = 'el8'
        elif 'centos' in base_image:
            log('Using RHEL (CentOS 7) Dockerfile template')
            template = 'rhel'
        elif ('ubuntu' in base_image or 'rocm' in base_image or
                'l4t-base' in base_image):
            log('Using Debian Dockerfile template')
            template = 'debian'
        else:
            raise RuntimeError(
                'cannot detect OS from image name: {}'.format(base_image))
        shutil.copy2(
            '{}/Dockerfile.{}'.format(docker_ctx, template),
            '{}/Dockerfile'.format(docker_ctx))

        python_versions = ' '.join(
            [x['pyenv'] for x in WHEEL_PYTHON_VERSIONS.values()])
        log('Building Docker image: {}'.format(image_tag))
        run_command(
            'docker', 'build',
            '--tag', image_tag,
            '--cache-from', image_tag,
            '--build-arg', 'BUILDKIT_INLINE_CACHE=1',
            '--build-arg', 'base_image={}'.format(base_image),
            '--build-arg', 'python_versions={}'.format(python_versions),
            '--build-arg', 'system_packages={}'.format(system_packages),
            docker_ctx,
            extra_env={'DOCKER_BUILDKIT': '1'},
        )
        if push:
            run_command('docker', 'push', image_tag)

    def _remove_container_image(self, image_tag):
        run_command('docker', 'rmi', image_tag)

    def _run_container(
            self, image_tag, kind, workdir, agent_args, *,
            require_runtime=True, docker_opts=None):
        assert kind in ('cuda', 'rocm')

        log('Running docker container with image: {} ({})'.format(
            image_tag, kind))
        docker_run = ['docker', 'run']
        if kind == 'cuda' and require_runtime:
            docker_run = ['nvidia-docker', 'run']
        elif kind == 'rocm':
            targets = os.environ.get('HCC_AMDGPU_TARGET', None)
            if targets is None:
                raise RuntimeError('HCC_AMDGPU_TARGET is not set')
            log('HCC_AMDGPU_TARGET = {}'.format(targets))
            docker_run += [
                '--env', 'HCC_AMDGPU_TARGET={}'.format(targets),
            ]
            if require_runtime:
                video_group = os.environ.get(
                    'CUPY_RELEASE_VIDEO_GROUP', 'video')
                docker_run += [
                    '--device=/dev/kfd', '--device=/dev/dri',
                ]
                if video_group != '':
                    docker_run += ['--group-add', video_group]
        command = docker_run + (docker_opts if docker_opts else []) + [
            '--rm',
            '--volume', '{}:/work'.format(workdir),
            '--workdir', '/work',
            image_tag,
        ] + agent_args
        run_command(*command)

    def _ensure_compatible_branch(self, version):
        if version.split('.')[0] != CUPY_MAJOR_VERSION:
            raise RuntimeError(
                'Version mismatch. cupy-release-tools is for CuPy v{} '
                'but your source tree is CuPy v{}.'.format(
                    CUPY_MAJOR_VERSION, version))

    def build_linux(
            self, target, cuda_version, python_version,
            source, output, dry_run, push, rmi):
        """Build a single wheel distribution for Linux."""

        version = get_version_from_source_tree(source)
        self._ensure_compatible_branch(version)

        if target == 'wheel-linux':
            assert cuda_version is not None
            log(
                'Starting wheel-linux build from {} '
                '(version {}, for CUDA {} + Python {})'.format(
                    source, version, cuda_version, python_version))
            action = 'bdist_wheel'
            image_tag = ('cupy/cupy-release-tools:builder-' +
                         f'{cuda_version}-v{CUPY_MAJOR_VERSION}')
            kind = WHEEL_LINUX_CONFIGS[cuda_version]['kind']
            arch = WHEEL_LINUX_CONFIGS[cuda_version].get('arch', 'x86_64')
            preloads = WHEEL_LINUX_CONFIGS[cuda_version]['preloads']
            platform_version = WHEEL_LINUX_CONFIGS[cuda_version].get(
                'platform_version', cuda_version)
            base_image = WHEEL_LINUX_CONFIGS[cuda_version]['image']
            builder_dockerfile = WHEEL_LINUX_CONFIGS[cuda_version].get(
                'builder_dockerfile', 'Dockerfile')
            package_name = WHEEL_LINUX_CONFIGS[cuda_version]['name']
            system_packages = \
                WHEEL_LINUX_CONFIGS[cuda_version]['system_packages']

            if kind == 'cuda':
                long_description_tmpl = WHEEL_LONG_DESCRIPTION_CUDA
            elif kind == 'rocm':
                long_description_tmpl = WHEEL_LONG_DESCRIPTION_ROCM
            else:
                assert False
            long_description = long_description_tmpl.format(
                version=platform_version)

            # Rename wheels to manylinux.
            asset_name = wheel_name(
                package_name, version, python_version,
                wheel_linux_platform_tag(arch, False))
            asset_dest_name = wheel_name(
                package_name, version, python_version,
                wheel_linux_platform_tag(arch, True))
        elif target == 'sdist':
            assert cuda_version is None
            log('Starting sdist build from {} (version {})'.format(
                source, version))
            action = 'sdist'
            image_tag = ('cupy/cupy-release-tools:builder-' +
                         f'sdist-v{CUPY_MAJOR_VERSION}')
            kind = 'cuda'
            arch = None
            preloads = []
            base_image = SDIST_CONFIG['image']
            builder_dockerfile = 'Dockerfile'
            package_name = 'cupy'
            system_packages = ''
            long_description = SDIST_LONG_DESCRIPTION

            # Rename not needed for sdist.
            asset_name = sdist_name('cupy', version)
            asset_dest_name = asset_name
        else:
            raise RuntimeError('unknown target')

        # Arguments for the agent.
        agent_args = [
            '--action', action,
            '--source', 'cupy',
            '--python', WHEEL_PYTHON_VERSIONS[python_version]['pyenv'],
            '--chown', '{}:{}'.format(os.getuid(), os.getgid()),
        ]

        # Add arguments to pass to setup.py.
        setup_args = [
            '--cupy-package-name', package_name,
            '--cupy-long-description', '../description.rst',
        ]
        if target == 'wheel-linux':
            setup_args += [
                '--cupy-no-rpath',
                '--cupy-wheel-metadata', '../_wheel.json',
            ]
            for lib in WHEEL_LINUX_CONFIGS[cuda_version]['libs']:
                setup_args += ['--cupy-wheel-lib', lib]
            for include_path, include_relpath in (
                    WHEEL_LINUX_CONFIGS[cuda_version]['includes']):
                spec = '{}:{}'.format(include_path, include_relpath)
                setup_args += ['--cupy-wheel-include', spec]
        elif target == 'sdist':
            setup_args += [
                '--cupy-no-cuda',
            ]

        agent_args += setup_args

        # Create a working directory.
        workdir = tempfile.mkdtemp(prefix='cupy-dist-')

        try:
            log('Using working directory: {}'.format(workdir))

            # Copy source tree to working directory.
            log('Copying source tree from: {}'.format(source))
            shutil.copytree(source, '{}/cupy'.format(workdir), symlinks=True)

            # Add long description file.
            with open('{}/description.rst'.format(workdir), 'w') as f:
                f.write(long_description)

            # Copy builder directory to working directory.
            docker_ctx = '{}/builder'.format(workdir)
            log('Copying builder directory to: {}'.format(docker_ctx))
            shutil.copytree('builder/', docker_ctx)

            # Extract optional CUDA libraries.
            optlib_workdir = '{}/cuda_lib'.format(docker_ctx)
            log('Creating CUDA optional lib directory under '
                'builder directory: {}'.format(optlib_workdir))
            os.mkdir(optlib_workdir)

            # Install CUDA optional libraries and generate a wheel metadata.
            if target == 'wheel-linux':
                wheel_metadata = {
                    'cuda': cuda_version,
                    'packaging': 'pip',
                }

                for p in preloads:
                    wheel_metadata[p] = prepare_cuda_opt_library(
                        p, cuda_version, optlib_workdir)
                log('Writing wheel metadata')
                with open('{}/_wheel.json'.format(workdir), 'w') as f:
                    json.dump(wheel_metadata, f)

            # Enable QEMU for cross-compilation.
            if arch is not None and arch != platform.uname().machine:
                log('Cross-build requested, registering binfmt interpreter')
                self._run_container(
                    'multiarch/qemu-user-static', kind, workdir,
                    ['--reset', '-p', 'yes'],
                    require_runtime=False,
                    docker_opts=['--privileged'],
                )

            # Creates a Docker image to build distribution.
            self._create_builder_linux(
                image_tag, base_image, builder_dockerfile, system_packages,
                docker_ctx, push)

            if dry_run:
                log('Dry run requested, exiting without actual build.')
                return

            # Build.
            log('Starting build')
            self._run_container(
                image_tag, kind, workdir, agent_args,
                require_runtime=False)
            log('Finished build')

            # Copy assets.
            asset_path = '{}/cupy/dist/{}'.format(workdir, asset_name)
            output_path = '{}/{}'.format(output, asset_dest_name)
            log('Copying asset from {} to {}'.format(asset_path, output_path))
            shutil.copy2(asset_path, output_path)

            # Remove Docker image.
            if rmi:
                log('Removing builder Docker image')
                self._remove_container_image(image_tag)

        finally:
            log('Removing working directory: {}'.format(workdir))
            shutil.rmtree(workdir)

    def _check_windows_environment(self, cuda_version, python_version):
        # Check if this script is running on Windows.
        if not sys.platform.startswith('win32'):
            raise RuntimeError(
                'you are on non-Windows system: {}'.format(sys.platform))

        # Check Python version.
        current_python_version = '.'.join(map(str, sys.version_info[0:2]))
        if python_version != current_python_version:
            raise RuntimeError(
                'Cannot build a wheel for Python {} using Python {}'.format(
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
            self, target, cuda_version, python_version,
            source, output):
        """Build a single wheel distribution for Windows.

        Note that Windows build is not isolated.
        """

        # Perform additional check as Windows environment is not isoalted.
        self._check_windows_environment(cuda_version, python_version)

        if target != 'wheel-win':
            raise ValueError('unknown target')

        version = get_version_from_source_tree(source)
        self._ensure_compatible_branch(version)

        log(
            'Starting wheel-win build from {} '
            '(version {}, for CUDA {} + Python {})'.format(
                source, version, cuda_version, python_version))

        action = 'bdist_wheel'
        preloads = WHEEL_WINDOWS_CONFIGS[cuda_version]['preloads']
        platform_version = WHEEL_LINUX_CONFIGS[cuda_version].get(
            'platform_version', cuda_version)
        package_name = WHEEL_WINDOWS_CONFIGS[cuda_version]['name']
        long_description = WHEEL_LONG_DESCRIPTION_CUDA.format(
            version=platform_version)
        asset_name = wheel_name(
            package_name, version, python_version, 'win_amd64')
        asset_dest_name = asset_name

        agent_args = [
            '--action', action,
            '--source', 'cupy',
        ]

        # Add arguments to pass to setup.py.
        setup_args = [
            '--cupy-package-name', package_name,
            '--cupy-long-description', '../description.rst',
        ]
        setup_args += ['--cupy-wheel-metadata', '../_wheel.json']
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

            # Copy source tree to working directory.
            log('Copying source tree from: {}'.format(source))
            shutil.copytree(source, '{}/cupy'.format(workdir))

            # Add long description file.
            with open('{}/description.rst'.format(workdir), 'w') as f:
                f.write(long_description)

            # Create a wheel metadata file for preload.
            wheel_metadata = {
                'cuda': cuda_version,
                'packaging': 'pip',
            }

            # Extract optional CUDA libraries.
            optlib_workdir = '{}/cuda_lib'.format(workdir)
            log('Creating CUDA optional lib directory under '
                'working directory: {}'.format(optlib_workdir))
            os.mkdir(optlib_workdir)
            for p in preloads:
                wheel_metadata[p] = prepare_cuda_opt_library(
                    p, cuda_version, optlib_workdir)

            # Create a wheel metadata file for preload.
            log('Writing wheel metadata')
            with open('{}/_wheel.json'.format(workdir), 'w') as f:
                json.dump(wheel_metadata, f)

            # Install optional CUDA libraries.
            log('Installing CUDA optional libraries')
            run_command(
                sys.executable,
                '{}/builder/setup_cuda_opt_lib.py'.format(os.getcwd()),
                '--src', optlib_workdir,
                '--dst', os.environ['CUDA_PATH'],
                cwd=workdir)

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
            self, target, cuda_version, python_version,
            dist, tests, dry_run, push, rmi):
        """Verify a single distribution for Linux."""

        if target == 'sdist':
            assert cuda_version is None
            image_tag = ('cupy/cupy-release-tools:verifier-' +
                         f'sdist-v{CUPY_MAJOR_VERSION}')
            kind = 'cuda'
            base_image = SDIST_CONFIG['verify_image']
            systems = SDIST_CONFIG['verify_systems']
            preloads = []
            system_packages = ''
        elif target == 'wheel-linux':
            assert cuda_version is not None
            image_tag = ('cupy/cupy-release-tools:verifier-' +
                         f'{cuda_version}-v{CUPY_MAJOR_VERSION}')
            kind = WHEEL_LINUX_CONFIGS[cuda_version]['kind']
            base_image = WHEEL_LINUX_CONFIGS[cuda_version]['verify_image']
            systems = WHEEL_LINUX_CONFIGS[cuda_version]['verify_systems']
            preloads = WHEEL_LINUX_CONFIGS[cuda_version]['preloads']
            system_packages = \
                WHEEL_LINUX_CONFIGS[cuda_version]['system_packages']
        else:
            raise RuntimeError('unknown target')

        for system in systems:
            image = base_image.format(system=system)
            image_tag_system = '{}-{}'.format(image_tag, system)
            log('Starting verification for {} on {} with Python {}'.format(
                dist, image, python_version))
            self._verify_linux(
                image_tag_system, image, kind, dist, tests,
                python_version,
                cuda_version, preloads, system_packages, dry_run, push, rmi)

    def _verify_linux(
            self, image_tag, base_image, kind, dist, tests, python_version,
            cuda_version, preloads, system_packages, dry_run, push, rmi):
        dist_basename = os.path.basename(dist)

        # Arguments for the agent.
        agent_args = [
            '--python', WHEEL_PYTHON_VERSIONS[python_version]['pyenv'],
            '--dist', dist_basename,
            '--chown', '{}:{}'.format(os.getuid(), os.getgid()),
        ]
        if 0 < len(preloads):
            agent_args += ['--cuda', cuda_version]
            for p in preloads:
                agent_args += ['--preload', p]

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
            log('Copying verifier directory to: {}'.format(docker_ctx))
            shutil.copytree('verifier/', docker_ctx)

            # Creates a Docker image to verify specified distribution.
            self._create_verifier_linux(
                image_tag, base_image, system_packages, docker_ctx, push)

            if dry_run:
                log('Dry run requested, exiting without actual verification.')
                return

            # Verify.
            log('Starting verification')
            self._run_container(image_tag, kind, workdir, agent_args)
            log('Finished verification')

            # Remove Docker image.
            if rmi:
                log('Removing verifier Docker image')
                self._remove_container_image(image_tag)

        finally:
            log('Removing working directory: {}'.format(workdir))
            shutil.rmtree(workdir)

    def verify_windows(
            self, target, cuda_version, python_version,
            dist, tests):
        """Verify a single distribution for Windows."""

        # Perform additional check as Windows environment is not isoalted.
        self._check_windows_environment(cuda_version, python_version)

        if target != 'wheel-win':
            raise ValueError('unknown target')

        preloads = WHEEL_WINDOWS_CONFIGS[cuda_version]['preloads']
        log('Starting verification for {} with Python {}'.format(
            dist, python_version))

        dist_basename = os.path.basename(dist)

        # Arguments for the agent.
        agent_args = [
            '--dist', dist,
        ]
        if 0 < len(preloads):
            agent_args += ['--cuda', cuda_version]
            for p in preloads:
                agent_args += ['--preload', p]

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
