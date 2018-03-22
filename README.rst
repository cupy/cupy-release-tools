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

* Linux
* ``nvidia-docker``
* ``tar`` with ``xz`` support
* ``dpkg``

To build wheels for Windows, you will need:

* Windows
* Visual Studio

Build
-----

This tool can be used to create both source distribution (``sdist``) and wheels.
To ensure the reproducibility of builds, the environment is isolated by Docker, and Cython version is specified explicitly.

Note that CuPy v4.0.0 / v5.0.0a1 or later is required to build wheels.

Wheel Matrix
~~~~~~~~~~~~

This tool builds wheels for Linux & Windows (x86_64) containing:

* CUDA 7.0 with cuDNN v4
* CUDA 7.5 with cuDNN v6 and NCCL v1
* CUDA 8.0 with cuDNN v7 and NCCL v2
* CUDA 9.0 with cuDNN v7 and NCCL v2

... for each of the following Python versions:

* 2.7
* 3.4
* 3.5
* 3.6

Preparing NCCL Assets for Linux
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When building a wheel, shared libraries (cuDNN / NCCL) are copied into the distribution.
cuDNN will be copied from the `base Docker image provided by NVIDIA <https://hub.docker.com/r/nvidia/cuda/>`_.
However, as the base image does not contain NCCL, you need to manually prepare the NCCL package.
NCCL is also required for sdist build to generate source that supports NCCL.

You can download the assets from `NCCL website <https://developer.nvidia.com/nccl>`_ (for NCCL 2.x) and `GitHub <https://github.com/NVIDIA/nccl/releases>`_ (for NCCL 1.x).
You can also use `nvget <https://github.com/kmaehashi/nvget>`_ to download NCCL 2.x using CLI.

::

  # NCCL 1.3.4 for CUDA 7.5
  wget "https://github.com/NVIDIA/nccl/releases/download/v1.2.3-1%2Bcuda7.5/libnccl1_1.2.3-1.cuda7.5_amd64.deb"
  wget "https://github.com/NVIDIA/nccl/releases/download/v1.2.3-1%2Bcuda7.5/libnccl-dev_1.2.3-1.cuda7.5_amd64.deb"

  # NCCL 2.1.4 for CUDA 8.0
  nvget --output "nccl_2.1.4-1+cuda8.0_x86_64.txz" "https://developer.nvidia.com/compute/machine-learning/nccl/secure/v2.1/prod/nccl_2.1.4-1cuda8.0_x86_64"

  # NCCL 2.1.4 for CUDA 9.0
  nvget --output "nccl_2.1.4-1+cuda9.0_x86_64.txz" "https://developer.nvidia.com/compute/machine-learning/nccl/secure/v2.1/prod/nccl_2.1.4-1cuda9.0_x86_64"

The directory containing the downloaded assets must be specified as ``--nccl-assets`` argument.

Building Distributions
~~~~~~~~~~~~~~~~~~~~~~

**IMPORTANT**: Always make sure to use a fresh, just-git-cloned source tree!
Otherwise the built distributions may not work.

To build a sdist, use the following command.
See the section above for ``--nccl-assets``.
``--source`` is a path to the source tree.

::

  ./dist.py --action build --target sdist --nccl-assets ~/nccl_assets --python 3.6.0 --source ~/dev/cupy

To build a wheel, use the following command.
This example builds wheel of CuPy with CUDA 8.0 for Python 3.6.

::

  ./dist.py --action build --target wheel-linux --nccl-assets ~/nccl_assets --python 3.6.0 --cuda 8.0 --source ~/dev/cupy

Working Directory
~~~~~~~~~~~~~~~~~

It is safe to run multiple ``dist.py`` at a time.
When building a distribution, a dedicated temporary directory (``/tmp/cupy-dist-XXXXX``) is created.
The temporary directory is shared with the builder docker container as a volume.
The working directory will be removed after the build.

Verify
------

The tool can be used to confirm that the built distribution will work with multiple environments.

Verifying Distributions
~~~~~~~~~~~~~~~~~~~~~~~

To verify the built distribution, use the following command:

::

  ./dist.py --action verify --target wheel-linux --nccl-assets ~/nccl_assets --python 3.6.0 --cuda 8.0 --dist cupy_cuda80-4.0.0b2-cp36-cp36m-linux_x86_64.whl --test release-tests/common --test release-tests/cudnn --test release-tests/nccl

You can specify test suites directory to ``--test`` argument.
``release-tests`` is a minimal test cases handy for final check before release.
Of course, you can also run the full unit test suites from CuPy source tree.

Publish
-------

Use ``twine`` command to upload distributions.
