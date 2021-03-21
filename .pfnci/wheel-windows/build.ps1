Param(
	[String]$python,
	[String]$cuda,
	[String]$branch,
	[String]$job_group
)

$ErrorActionPreference = "Stop"
. "$PSScriptRoot\_error_handler.ps1"

. "$PSScriptRoot\_flexci.ps1"

PrioritizeFlexCIDaemon

# Configure environment
ActivatePython ($python.Split(".")[0..1] -join ".")
ActivateCUDA $cuda

$cuda_path = $Env:CUDA_PATH

# Show build configuration
echo ">> Environment Variables"
echo "     CUDA_PATH:   $cuda_path"
echo "     PATH:        $Env:PATH"
echo ">> Python Version:"
RunOrDie python -V

# Remove existing cuDNN installation
echo "Uninstalling existing cuDNN installation from ${cuda_path}"
Remove-Item -Force -Verbose ${cuda_path}\bin\cudnn*.dll
Remove-Item -Force -Verbose ${cuda_path}\include\cudnn*.h
Remove-Item -Force -Verbose ${cuda_path}\lib\x64\cudnn*.lib

# Clone CuPy and checkout the target branch
RunOrDie git clone --recursive --branch $branch --depth 1 https://github.com/cupy/cupy.git cupy

# Install dependencies
echo ">> Installing dependences for wheel build..."
RunOrDie python -m pip install -U wheel Cython pytest
echo ">> Packages installed:"
RunOrDie python -m pip list

# Build
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

# Verify
echo ">> Starting verification..."
RunOrDie python ./dist.py --action verify --target wheel-win --python $python --cuda $cuda --dist $wheel_file --test release-tests/common --test release-tests/cudnn --test release-tests/pkg_wheel

# Show build configuration in CuPy
echo ">> Build configuration"
RunOrDie python -c "import cupy; cupy.show_config()"

# Upload to GCS
echo ">> Uploading an artifact..."
RunOrDie gsutil -m cp $wheel_file gs://tmp-asia-pfn-public-ci/cupy-release-tools/build-windows/${job_group}_${branch}/${Env:FLEXCI_JOB_ID}_py${python}_cuda${cuda}/

echo ">> Done!"
