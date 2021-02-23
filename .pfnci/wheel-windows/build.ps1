Param(
	[String]$python,
	[String]$cuda
)

$ErrorActionPreference = "Stop"
. "$PSScriptRoot\_error_handler.ps1"

# Set environment variables.
$python_path = $null
switch ($python) {
    "3.6.0" {
        $python_path = "C:\Development\Python\Python36"
    }
    "3.7.0" {
        $python_path = "C:\Development\Python\Python37"
    }
    "3.8.0" {
        $python_path = "C:\Development\Python\Python38"
    }
    "3.9.0" {
        $python_path = "C:\Development\Python\Python39"
    }
    default {
         throw "Unsupported Python version: $python"
    }
}

$cuda_path = $null
switch ($cuda) {
    "8.0" {
        $cuda_path = $Env:CUDA_PATH_V8_0
    }
    "9.0" {
        $cuda_path = $Env:CUDA_PATH_V9_0
    }
    "9.1" {
        $cuda_path = $Env:CUDA_PATH_V9_1
    }
    "9.2" {
        $cuda_path = $Env:CUDA_PATH_V9_2
    }
    "10.0" {
        $cuda_path = $Env:CUDA_PATH_V10_0
    }
    "10.1" {
        $cuda_path = $Env:CUDA_PATH_V10_1
    }
    "10.2" {
        $cuda_path = $Env:CUDA_PATH_V10_2
    }
    "11.0" {
        $cuda_path = $Env:CUDA_PATH_V11_0
    }
    "11.1" {
        $cuda_path = $Env:CUDA_PATH_V11_1
    }
    default {
         throw "Unsupported CUDA version: $cuda"
    }
}

$Env:PYTHON_PATH = ${python_path}
$Env:CUDA_PATH = ${cuda_path}
$Env:PATH = "${python_path};${python_path}\Scripts;${cuda_path}\bin;$Env:ProgramFiles\NVIDIA Corporation\NvToolsExt\bin\x64;$Env:PATH"

# Show build configuration
echo ">> Environment Variables"
echo "     PYTHON_PATH: $Env:PYTHON_PATH"
echo "     CUDA_PATH:   $Env:CUDA_PATH"
echo "     PATH:        $Env:PATH"
echo ">> Python Version:"
RunOrDie python -V

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
RunOrDie python -c "import cupy; cupy.show_config()"
echo ">> Build completed."
