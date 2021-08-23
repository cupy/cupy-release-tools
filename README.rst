cupy-release-tools
==================

Tools to automate the CuPy release process.

The release process consists of 3 steps:

1. Build
2. Verify
3. Publish

Requirements
------------

To build ``sdist`` and wheels for Linux, you will need:

* Linux with Docker support
* Docker
* For CUDA build:
    * ``nvidia-docker``
    * ``tar`` with ``xz`` support

To build wheels for Windows, you will need:

* Windows
* Visual C++

Quick Guide
-----------

You can use the following shell scripts that wrap the process on Linux.

::

  # Prepare source tree
  git clone --recursive https://github.com/cupy/cupy.git

  # Build & verify a sdist (using Python 3.7)
  ./build.sh sdist 3.7

  # Build & verify a wheel for CUDA 11.0 + Python 3.8
  ./build.sh 11.0 3.8

For Windows, or if you need some more detailed configuration, see the sections below to manually run the tool.

Build
-----

This tool can be used to create both source distribution (``sdist``) and wheels.
To ensure the reproducibility of builds, the environment is isolated by Docker on Linux.

Wheel Matrix
~~~~~~~~~~~~

This tool builds wheels for Linux & Windows (x86_64) for the matrix of all supported CUDA X Python variants, defined in ``dist_config.py``.

Building Distributions
~~~~~~~~~~~~~~~~~~~~~~

**IMPORTANT**: Always make sure to use a fresh, just-git-cloned CuPy source tree!

To build a sdist, use the following command.
``--source`` is a path to the source tree.

::

  ./dist.py --action build --target sdist --python 3.6.0 --source path/to/cupy_repo

To build a wheel, use the following command.
This example builds wheel of CuPy with CUDA 10.0 for Python 3.8.

::

  ./dist.py --action build --target wheel-linux --python 3.8 --cuda 10.0 --source path/to/cupy_repo

Use ``--target wheel-win`` for Windows build.
Use ``--cuda rocm-4.3`` for ROCm (AMD GPU) build.

Working Directory
~~~~~~~~~~~~~~~~~

It is safe to run multiple ``dist.py`` at a time.
Each time you run the tool, a dedicated temporary directory (``/tmp/cupy-dist-XXXXX``) is created.
The temporary directory is shared with the builder docker container as a volume.
The working directory will be removed after the build.

The resulting asset (sdist/wheel) will be copied back to the current directory.

Verify
------

The tool can be used to confirm that the built distribution will work with multiple environments.

Verifying Distributions
~~~~~~~~~~~~~~~~~~~~~~~

To verify the built distribution, use the following command:

::

  ./dist.py --action verify --target wheel-linux --python 3.8 --cuda 10.0 --dist cupy_cuda100-9.0.0b2-cp38-cp38-manylinux_x86_64.whl --test release-tests/common --test release-tests/cudnn --test release-tests/nccl

You can specify test suites directory to ``--test`` argument.
``release-tests`` is a minimal test cases handy for final check before release.
Of course, you can also run the full unit test suites from CuPy source tree.

Publish
-------

Use ``twine`` command to upload distributions.
