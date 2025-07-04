#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import time
import typing
from contextlib import contextmanager
from typing import Any, Literal

import tomli
import tomli_w

from dist_config import (
    CUPY_MAJOR_VERSION,
    CYTHON_VERSION,
    FASTRLOCK_VERSION,
    SDIST_CONFIG,
    SDIST_LONG_DESCRIPTION,
    WHEEL_LINUX_CONFIGS,
    WHEEL_LONG_DESCRIPTION_CUDA,
    WHEEL_LONG_DESCRIPTION_ROCM,
    WHEEL_PYTHON_VERSIONS,
    WHEEL_WINDOWS_CONFIGS,
)  # NOQA
from dist_utils import (
    get_system_cuda_version,
    get_version_from_source_tree,
    sdist_name,
    wheel_linux_platform_tag,
    wheel_name,
)  # NOQA

if typing.TYPE_CHECKING:
    from collections.abc import Collection, Iterable, Iterator, Mapping


def log(msg: str) -> None:
    print(f'[{time.asctime()}]: {msg}', flush=True)


@contextmanager
def log_group(title: str) -> Iterator[None]:
    """
    Emits a log group (for GitHub Actions).
    """
    print(f'::group::{title}')
    yield
    print('::endgroup::')


def run_command(
    *cmd: str,
    extra_env: Mapping[str, str] | None = None,
    cwd: str | None = None,
) -> None:
    env = None
    if extra_env is not None:
        env = os.environ.copy()
        env.update(extra_env)
    log(f'Running command: {cmd}')
    subprocess.check_call(cmd, env=env, cwd=cwd, encoding='UTF-8')


def run_command_output(*cmd: str, cwd: str | None = None) -> str:
    log(f'Running command: {cmd}')
    return subprocess.check_output(cmd, cwd=cwd, encoding='UTF-8')


def generate_wheel_metadata(
    libraries: list[str], cuda_version: str,
) -> dict[str, Any]:
    machine = platform.machine()
    if machine == 'AMD64':  # Windows
        machine = 'x86_64'
    target_system = f'{platform.system()}:{machine}'
    log(
        f'Generating preloading metadata for CUDA '
        f'{cuda_version} / {target_system}'
    )
    command = [
        sys.executable,
        'cupy/cupyx/tools/_generate_wheel_metadata.py',
        '--cuda', cuda_version,
        '--target', target_system,
    ]
    for library in libraries:
        command += ['--library', library]

    ret: dict[str, Any] = json.loads(run_command_output(*command))
    return ret


def install_cuda_opt_library(
    library: str, cuda_version: str, arch: str, prefix: str, *, workdir: str
) -> None:
    """Installs the library to the prefix."""
    command = [
        sys.executable,
        'cupy/cupyx/tools/install_library.py',
        '--library', library,
        '--cuda', cuda_version,
        '--arch', arch,
        '--prefix', prefix,
    ]
    log(f'Extracting the library to {prefix}')
    run_command(*command, '--action', 'install', cwd=workdir)


def rename_project(src: str, name: str) -> None:
    """Rename project.name in pyproject.toml."""
    assert src.endswith('pyproject.toml')
    log(f'Renaming project name to {name} ({src})')
    with open(src, 'rb') as f:
        pp = tomli.load(f)
    pp['project']['name'] = name
    with open(src, 'wb') as f:
        tomli_w.dump(pp, f)


class _ControllerArgs(argparse.Namespace):
    action: Literal['build', 'verify']
    target: Literal['sdist', 'wheel-linux', 'wheel-win']
    cuda: str | None
    python: str
    dry_run: bool
    push: bool
    rmi: bool
    source: str | None
    output: str
    dist: str | None
    test: list[str]


class Controller:
    @staticmethod
    def parse_args() -> _ControllerArgs:
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

        return parser.parse_args(namespace=_ControllerArgs())

    def main(self) -> None:
        args = self.parse_args()

        if args.action == 'build':
            assert args.source is not None
            with log_group('Build'):
                if args.target == 'wheel-win':
                    assert args.cuda is not None, 'CUDA version unspecified'
                    self.build_windows(
                        args.target, args.cuda, args.python,
                        args.source, args.output)
                else:
                    # For sdist build, args.cuda can be None.
                    self.build_linux(
                        args.target, args.cuda, args.python,
                        args.source, args.output, args.dry_run, args.push,
                        args.rmi)
        elif args.action == 'verify':
            assert args.dist is not None
            if args.target == 'wheel-win':
                assert args.cuda is not None, 'CUDA version unspecified'
                with log_group('Verify'):
                    self.verify_windows(
                        args.target, args.cuda, args.python,
                        args.dist, args.test)
            else:
                # Log group will be emit for each verification run.
                # For sdist verify, args.cuda can be None.
                self.verify_linux(
                    args.target, args.cuda, args.python,
                    args.dist, args.test, args.dry_run, args.push,
                    args.rmi)

    @staticmethod
    def _create_builder_linux(
        image_tag: str,
        base_image: str,
        builder_dockerfile: str,
        system_packages: str,
        docker_ctx: str,
        push: bool,
    ) -> None:
        """Create a docker image to build distributions."""

        python_versions = ' '.join(
            [x['pyenv'] for x in WHEEL_PYTHON_VERSIONS.values()])
        log(f'Building Docker image: {image_tag}')
        run_command(
            'docker', 'build',
            '--file', f'{docker_ctx}/{builder_dockerfile}',
            '--tag', image_tag,
            '--cache-from', image_tag,
            '--build-arg', 'BUILDKIT_INLINE_CACHE=1',
            '--build-arg', f'base_image={base_image}',
            '--build-arg', f'python_versions={python_versions}',
            '--build-arg', f'cython_version={CYTHON_VERSION}',
            '--build-arg', f'fastrlock_version={FASTRLOCK_VERSION}',
            '--build-arg', f'system_packages={system_packages}',
            docker_ctx,
            extra_env={'DOCKER_BUILDKIT': '1'},
        )
        if push:
            run_command('docker', 'push', image_tag)

    @staticmethod
    def _create_verifier_linux(
        image_tag: str,
        base_image: str,
        system_packages: str,
        docker_ctx: str,
        push: bool,
    ) -> None:
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
                f'cannot detect OS from image name: {base_image}')
        shutil.copy2(
            f'{docker_ctx}/Dockerfile.{template}',
            f'{docker_ctx}/Dockerfile')

        python_versions = ' '.join(
            [x['pyenv'] for x in WHEEL_PYTHON_VERSIONS.values()])
        log(f'Building Docker image: {image_tag}')
        run_command(
            'docker', 'build',
            '--tag', image_tag,
            '--cache-from', image_tag,
            '--build-arg', 'BUILDKIT_INLINE_CACHE=1',
            '--build-arg', f'base_image={base_image}',
            '--build-arg', f'python_versions={python_versions}',
            '--build-arg', f'system_packages={system_packages}',
            docker_ctx,
            extra_env={'DOCKER_BUILDKIT': '1'},
        )
        if push:
            run_command('docker', 'push', image_tag)

    @staticmethod
    def _remove_container_image(image_tag: str) -> None:
        run_command('docker', 'rmi', '-f', image_tag)

    @staticmethod
    def _run_container(
        image_tag: str,
        kind: Literal['cuda', 'rocm'],
        workdir: str,
        agent_args: list[str],
        *,
        require_runtime: bool = True,
        docker_opts: list[str] | None = None,
    ) -> None:
        assert kind in {'cuda', 'rocm'}

        log(f'Running docker container with image: {image_tag} ({kind})')
        docker_run = ['docker', 'run']
        if kind == 'cuda' and require_runtime:
            docker_run += ['--gpus=all']
        elif kind == 'rocm':
            targets = os.environ.get('HCC_AMDGPU_TARGET', None)
            if targets is None:
                raise RuntimeError('HCC_AMDGPU_TARGET is not set')
            log(f'HCC_AMDGPU_TARGET = {targets}')
            docker_run += [
                '--env', f'HCC_AMDGPU_TARGET={targets}',
            ]
            if require_runtime:
                video_group = os.environ.get(
                    'CUPY_RELEASE_VIDEO_GROUP', 'video')
                docker_run += [
                    '--device=/dev/kfd', '--device=/dev/dri',
                ]
                if video_group != '':
                    docker_run += ['--group-add', video_group]
        command = (
            docker_run
            + (docker_opts if docker_opts is not None else [])
            + [
                '--rm',
                '--volume',
                f'{workdir}:/work',
                '--workdir',
                '/work',
                image_tag,
            ]
            + agent_args
        )
        run_command(*command)

    @staticmethod
    def _ensure_compatible_branch(version: str) -> None:
        if version.split('.')[0] != CUPY_MAJOR_VERSION:
            raise RuntimeError(
                'Version mismatch. '
                f'cupy-release-tools is for CuPy v{CUPY_MAJOR_VERSION} '
                f'but your source tree is CuPy v{version}.'
            )

    def build_linux(
        self,
        target: str,
        cuda_version: str | None,
        python_version: str,
        source: str,
        output: str,
        dry_run: bool,
        push: bool,
        rmi: bool,
    ) -> None:
        """Build a single wheel distribution for Linux."""

        version = get_version_from_source_tree(source)
        self._ensure_compatible_branch(version)

        if target == 'wheel-linux':
            assert cuda_version is not None
            log(
                f'Starting wheel-linux build from {source} '
                f'(version {version}, for CUDA {cuda_version} '
                f'+ Python {python_version})'
            )
            action = 'wheel'
            image_tag = ('cupy/cupy-release-tools:builder-'
                         f'{cuda_version}-v{CUPY_MAJOR_VERSION}')
            kind = WHEEL_LINUX_CONFIGS[cuda_version]['kind']
            arch = WHEEL_LINUX_CONFIGS[cuda_version].get('arch', 'x86_64')
            preloads = WHEEL_LINUX_CONFIGS[cuda_version]['preloads']
            preloads_cuda_version = WHEEL_LINUX_CONFIGS[cuda_version].get(
                'preloads_cuda_version', cuda_version)
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
                raise AssertionError('Unreachable')
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
            log(f'Starting sdist build from {source} (version {version})')
            action = 'sdist'
            image_tag = ('cupy/cupy-release-tools:builder-'
                         f'sdist-v{CUPY_MAJOR_VERSION}')
            kind = 'cuda'
            arch = None
            preloads = []
            preloads_cuda_version = None
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
            '--chown', f'{os.getuid()}:{os.getgid()}',
        ]

        # Environmental variables to pass to builder
        setup_args = ['--env', 'CUPY_INSTALL_LONG_DESCRIPTION=../description.rst']
        if target == 'wheel-linux':
            setup_args += [
                '--env',
                'CUPY_INSTALL_NO_RPATH=1',
                '--env',
                'CUPY_INSTALL_WHEEL_METADATA=../_wheel.json',
            ]
        elif target == 'sdist':
            setup_args += ['--env', 'CUPY_INSTALL_USE_STUB=1']
        agent_args += setup_args

        # Create a working directory.
        workdir = tempfile.mkdtemp(prefix='cupy-dist-')

        try:
            log(f'Using working directory: {workdir}')

            # Copy source tree to working directory.
            log(f'Copying source tree from: {source}')
            shutil.copytree(source, f'{workdir}/cupy', symlinks=True)

            # Rename project name
            rename_project(f'{workdir}/cupy/pyproject.toml', package_name)

            # Add long description file.
            with open(
                f'{workdir}/description.rst', 'w', encoding='UTF-8'
            ) as f:
                f.write(long_description)

            # Copy builder directory to working directory.
            docker_ctx = f'{workdir}/builder'
            log(f'Copying builder directory to: {docker_ctx}')
            shutil.copytree('builder/', docker_ctx)

            # Extract optional CUDA libraries.
            optlib_workdir = f'{docker_ctx}/cuda_lib'
            log('Creating CUDA optional lib directory under '
                f'builder directory: {optlib_workdir}')
            os.mkdir(optlib_workdir)
            for p in preloads:
                assert preloads_cuda_version is not None
                assert arch is not None
                install_cuda_opt_library(
                    p, preloads_cuda_version, arch, optlib_workdir,
                    workdir=workdir)

            # Create a wheel metadata file for preload.
            if target == 'wheel-linux':
                assert preloads_cuda_version is not None
                wheel_metadata = generate_wheel_metadata(
                    preloads, preloads_cuda_version)
                log('Writing wheel metadata')
                with open(
                    f'{workdir}/_wheel.json', 'w', encoding='UTF-8'
                ) as f:
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
            asset_path = f'{workdir}/cupy/dist/{asset_name}'
            output_path = f'{output}/{asset_dest_name}'
            log(f'Copying asset from {asset_path} to {output_path}')
            shutil.copy2(asset_path, output_path)

            # Remove Docker image.
            if rmi:
                log('Removing builder Docker image')
                self._remove_container_image(image_tag)

        finally:
            log(f'Removing working directory: {workdir}')
            shutil.rmtree(workdir)

    @staticmethod
    def _check_windows_environment(
        cuda_version: str, python_version: str
    ) -> None:
        # Check if this script is running on Windows.
        if not sys.platform.startswith('win32'):
            raise RuntimeError(
                f'you are on non-Windows system: {sys.platform}')

        # Check Python version.
        current_python_version = '.'.join(map(str, sys.version_info[0:2]))
        if python_version != current_python_version:
            raise RuntimeError(
                f'Cannot build a wheel for Python {python_version} '
                f'using Python {current_python_version}')

        # Check CUDA runtime version.
        config = WHEEL_WINDOWS_CONFIGS[cuda_version]
        cuda_check_version = config['check_version']
        current_cuda_version = get_system_cuda_version(config['cudart_lib'])
        if current_cuda_version is None:
            raise RuntimeError(
                'Cannot build wheel without CUDA Runtime installed')
        if not cuda_check_version(current_cuda_version):
            raise RuntimeError(
                f'Cannot build wheel for CUDA {cuda_version} '
                f'using CUDA {current_cuda_version}')

    def build_windows(
        self,
        target: str,
        cuda_version: str,
        python_version: str,
        source: str,
        output: str,
    ) -> None:
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
            f'Starting wheel-win build from {source} '
            f'(version {version}, for CUDA {cuda_version} '
            f'+ Python {python_version})')

        action = 'wheel'
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

        # Environmental variables to pass to builder
        agent_args += [
            '--env',
            'CUPY_INSTALL_LONG_DESCRIPTION=../description.rst',
            '--env',
            'CUPY_INSTALL_WHEEL_METADATA=../_wheel.json',
        ]

        # Create a working directory.
        workdir = tempfile.mkdtemp(prefix='cupy-dist-')

        try:
            log(f'Using working directory: {workdir}')

            # Copy source tree to working directory.
            log(f'Copying source tree from: {source}')
            shutil.copytree(source, f'{workdir}/cupy')

            # Rename project name
            rename_project(f'{workdir}/cupy/pyproject.toml', package_name)

            # Add long description file.
            with open(
                f'{workdir}/description.rst', 'w', encoding='UTF-8'
            ) as f:
                f.write(long_description)

            # Extract optional CUDA libraries.
            optlib_workdir = f'{workdir}/cuda_lib'
            log('Creating CUDA optional lib directory under '
                f'working directory: {optlib_workdir}')
            os.mkdir(optlib_workdir)
            for p in preloads:
                install_cuda_opt_library(
                    p, cuda_version, 'x86_64', optlib_workdir,
                    workdir=workdir)

            # Create a wheel metadata file for preload.
            log('Creating wheel metadata')
            wheel_metadata = generate_wheel_metadata(preloads, cuda_version)
            log('Writing wheel metadata')
            with open(f'{workdir}/_wheel.json', 'w', encoding='UTF-8') as f:
                json.dump(wheel_metadata, f)

            # Install optional CUDA libraries.
            log('Installing CUDA optional libraries')
            run_command(
                sys.executable,
                f'{os.getcwd()}/builder/setup_cuda_opt_lib.py',
                '--src', optlib_workdir,
                '--dst', os.environ['CUDA_PATH'],
                cwd=workdir)

            # Build.
            log('Starting build')
            run_command(
                sys.executable, f'{os.getcwd()}/builder/agent.py',
                *agent_args, cwd=workdir)
            log('Finished build')

            # Copy assets.
            asset_path = f'{workdir}/cupy/dist/{asset_name}'
            output_path = f'{output}/{asset_dest_name}'
            log(f'Copying asset from {asset_path} to {output_path}')
            shutil.copy2(asset_path, output_path)

        finally:
            log(f'Removing working directory: {workdir}')
            try:
                shutil.rmtree(workdir)
            except OSError as e:
                # TODO(kmaehashi): On Windows, removal of `.git` directory may
                # fail with PermissionError (on Python 3) or OSError (on
                # Python 2). Note that PermissionError inherits OSError.
                log(f'Failed to clean-up working directory: {e}\n\n'
                    f'Please remove the working directory manually: {workdir}')

    def verify_linux(
        self,
        target: Literal['sdist', 'wheel-linux'],
        cuda_version: str | None,
        python_version: str,
        dist: str,
        tests: Iterable[str],
        dry_run: bool,
        push: bool,
        rmi: bool,
    ) -> None:
        """Verify a single distribution for Linux."""

        kind: Literal['cuda', 'rocm']
        if target == 'sdist':
            assert cuda_version is None
            image_tag = ('cupy/cupy-release-tools:verifier-'
                         f'sdist-v{CUPY_MAJOR_VERSION}')
            kind = 'cuda'
            base_image = SDIST_CONFIG['verify_image']
            systems = SDIST_CONFIG['verify_systems']
            preloads = []
            system_packages = ''
        elif target == 'wheel-linux':
            assert cuda_version is not None
            image_tag = ('cupy/cupy-release-tools:verifier-'
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
            with log_group(f'Verify: {dist} ({system} / Py {python_version})'):
                image = base_image.format(system=system)
                image_tag_system = f'{image_tag}-{system}'
                log(f'Starting verification for {dist} on {image} '
                    f'with Python {python_version}')
                self._verify_linux(
                    image_tag_system, image, kind, dist, tests,
                    python_version,
                    cuda_version, preloads, system_packages, dry_run, push,
                    rmi)

    def _verify_linux(
        self,
        image_tag: str,
        base_image: str,
        kind: Literal['cuda', 'rocm'],
        dist: str,
        tests: Iterable[str],
        python_version: str,
        cuda_version: str | None,
        preloads: Collection[str],
        system_packages: str,
        dry_run: bool,
        push: bool,
        rmi: bool,
    ) -> None:
        dist_basename = os.path.basename(dist)

        # Arguments for the agent.
        agent_args = [
            '--python', WHEEL_PYTHON_VERSIONS[python_version]['pyenv'],
            '--dist', dist_basename,
            '--chown', f'{os.getuid()}:{os.getgid()}',
        ]
        if 0 < len(preloads):
            assert cuda_version is not None
            agent_args += ['--cuda', cuda_version]
            for p in preloads:
                agent_args += ['--preload', p]

        # Add arguments for `python -m pytest`.
        agent_args += ['tests']

        # Create a working directory.
        workdir = tempfile.mkdtemp(prefix='cupy-dist-')

        try:
            log(f'Using working directory: {workdir}')

            # Copy dist and tests to working directory.
            log(f'Copying distribution from: {dist}')
            shutil.copy2(dist, f'{workdir}/{dist_basename}')
            tests_dir = f'{workdir}/tests'
            os.mkdir(tests_dir)
            for test in tests:
                log(f'Copying tests from: {test}')
                shutil.copytree(
                    test,
                    f'{tests_dir}/{os.path.basename(test)}')

            # Copy verifier directory to working directory.
            docker_ctx = f'{workdir}/verifier'
            log(f'Copying verifier directory to: {docker_ctx}')
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
            log(f'Removing working directory: {workdir}')
            shutil.rmtree(workdir)

    def verify_windows(
        self,
        target: str,
        cuda_version: str,
        python_version: str,
        dist: str,
        tests: Iterable[str],
    ) -> None:
        """Verify a single distribution for Windows."""

        # Perform additional check as Windows environment is not isoalted.
        self._check_windows_environment(cuda_version, python_version)

        if target != 'wheel-win':
            raise ValueError('unknown target')

        preloads = WHEEL_WINDOWS_CONFIGS[cuda_version]['preloads']
        log(f'Starting verification for {dist} with Python {python_version}')

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
            log(f'Using working directory: {workdir}')

            # Copy dist and tests to working directory.
            log(f'Copying distribution from: {dist}')
            shutil.copy2(dist, f'{workdir}/{dist_basename}')
            tests_dir = f'{workdir}/tests'
            os.mkdir(tests_dir)
            for test in tests:
                log(f'Copying tests from: {test}')
                shutil.copytree(
                    test,
                    f'{tests_dir}/{os.path.basename(test)}')

            # Verify.
            log('Starting verification')
            run_command(
                sys.executable, f'{os.getcwd()}/verifier/agent.py',
                *agent_args, cwd=workdir)
            log('Finished verification')

        finally:
            log(f'Removing working directory: {workdir}')
            shutil.rmtree(workdir)


if __name__ == '__main__':
    Controller().main()
