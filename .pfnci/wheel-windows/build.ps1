Param(
	[String]$cuda,
	[String]$python,
	[String]$branch,
	[String]$job_group
)

$ErrorActionPreference = "Stop"
. "$PSScriptRoot\_error_handler.ps1"

. "$PSScriptRoot\_flexci.ps1"

PrioritizeFlexCIDaemon
EnableLongPaths

function UninstallCuDNN($cuda_path) {
    echo "Uninstalling cuDNN installation from ${cuda_path}"
    Remove-Item -Force -Verbose ${cuda_path}\bin\cudnn*.dll
    Remove-Item -Force -Verbose ${cuda_path}\include\cudnn*.h
    Remove-Item -Force -Verbose ${cuda_path}\lib\x64\cudnn*.lib
}

function UninstallCuTENSOR($cuda_path) {
    echo "Uninstalling cuTENSOR installation from ${cuda_path}"
    if(Test-Path ${cuda_path}\bin\cutensor.dll) {
        Remove-Item -Force -Verbose ${cuda_path}\bin\cutensor.dll
        Remove-Item -Force -Verbose ${cuda_path}\bin\cutensor.lib
        Remove-Item -Force -Verbose ${cuda_path}\bin\cutensor_static.lib
        Remove-Item -Force -Verbose ${cuda_path}\include\cutensor.h
        Remove-Item -Recurse -Force -Verbose ${cuda_path}\include\cutensor
    } else {
       echo "cuTENSOR installation not detected"
    }
}

# Activate target CUDA/cuDNN/Python
ActivateCUDA $cuda
$cuda_path = $Env:CUDA_PATH
$has_cudnn = ($cuda.startswith("11.") -or $cuda.startswith("12."))
if ($has_cudnn) {
    ActivateCuDNN "8.8" $cuda
}
ActivatePython $python

# Show build configuration
echo ">> Environment Variables"
echo "     CUDA_PATH:   $cuda_path"
echo "     PATH:        $Env:PATH"
echo ">> Python Version:"
RunOrDie python -V

# Clone CuPy and checkout the target branch
if ($Env:CUPY_RELEASE_NO_CLONE -eq "1") {
    echo ">> CUPY_RELEASE_NO_CLONE=1 is set. Using CuPy source tree in the current directory"
} else {
    echo ">> Cloning CuPy..."
    if ($branch -eq "") {
        $branch = Get-Content "./.pfnci/BRANCH"
        echo ">> Using CuPy branch that matches with the current cupy-release-tools: $branch"
    } else {
        echo ">> Using specified CuPy branch: $branch"
    }
    RunOrDie git clone --recursive --branch $branch --depth 1 https://github.com/cupy/cupy.git cupy
    RunOrDie git -C cupy config core.symlinks true
    RunOrDie git -C cupy reset --hard
}

# Get tool versions from configuration.
$cython_version = @(python -c "import dist_config; print(dist_config.CYTHON_VERSION)")
$fastrlock_version = @(python -c "import dist_config; print(dist_config.FASTRLOCK_VERSION)")

# Install dependencies
echo ">> Updating packaging utilities..."
RunOrDie python -m pip install -U setuptools pip
echo ">> Installing dependences for wheel build..."
RunOrDie python -m pip install -U -r ./requirements.txt wheel Cython==${cython_version} fastrlock==${fastrlock_version} pytest
echo ">> Packages installed:"
RunOrDie python -m pip list

# Build
# Note: cuDNN and cuTENSOR will be installed by the tool.
echo ">> Starting build..."
RunOrDie python ./dist.py --action build --target wheel-win --source cupy --python $python --cuda $cuda

# Get wheel name
$dist_config = @(
    python .\get_dist_info.py --target wheel-win --source cupy --python $python --cuda $cuda `
    | ConvertFrom-Csv -Delimiter "=" -Header "Key", "Value"
)
$wheel_file = $dist_config[0].Value
echo ">> Wheel File: ${wheel_file}"

# List files
Get-ChildItem

# Uninstall cuDNN and cuTENSOR
UninstallCuDNN $cuda_path
UninstallCuTENSOR $cuda_path

# Install dependency for cuDNN 8.3+
if ($has_cudnn) {
    echo ">> Installing zlib"
    InstallZLIB
}

# Verify
echo ">> Validating with twine check..."
RunOrDie python -m twine check --strict $wheel_file
echo ">> Starting verification..."
if ($has_cudnn) {
    RunOrDie python ./dist.py --action verify --target wheel-win --python $python --cuda $cuda --dist $wheel_file --test release-tests/common --test release-tests/cudnn --test release-tests/pkg_wheel
} else {
    RunOrDie python ./dist.py --action verify --target wheel-win --python $python --cuda $cuda --dist $wheel_file --test release-tests/common --test release-tests/pkg_wheel
}

# Show build configuration in CuPy
echo ">> Build configuration"
RunOrDie python -c "import cupy; cupy.show_config()"

# Upload to GCS
if ($job_group -eq "") {
    echo ">> Upload skipped as job group is not specified"
} else {
    $url = "gs://tmp-asia-pfn-public-ci/cupy-release-tools/build-windows/${job_group}_${branch}/${Env:FLEXCI_JOB_ID}_py${python}_cuda${cuda}/"
    echo ">> Uploading an artifact: $url"
    RunOrDie gsutil -m cp $wheel_file $url
}

echo ">> Done!"
