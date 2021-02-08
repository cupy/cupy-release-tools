Param(
	[String]$cuda
)

$ErrorActionPreference = "Stop"

function install_cudnn([String]$cudnn_zip, [String]$cuda_root) {
  echo "Uninstalling existing cuDNN installation from ${cuda_root}"
  Remove-Item -Force -Verbose ${cuda_root}\bin\cudnn*.dll
  Remove-Item -Force -Verbose ${cuda_root}\include\cudnn*.h
  Remove-Item -Force -Verbose ${cuda_root}\lib\x64\cudnn*.lib

  echo "Installing ${cudnn_zip} to ${cuda_root}..."
  Remove-Item -Recurse -Force -ErrorAction:SilentlyContinue tmp_cudnn
  Expand-Archive -Path ${cudnn_zip} -DestinationPath tmp_cudnn
  Push-Location tmp_cudnn
  Move-Item -Force cuda\bin\* ${cuda_root}\bin
  Move-Item -Force cuda\include\* ${cuda_root}\include
  Move-Item -Force cuda\lib\x64\* ${cuda_root}\lib\x64
  Pop-Location
  Remove-Item -Recurse -Force tmp_cudnn
}

switch ($cuda) {
    "8.0" {
        $cuda_path = $Env:CUDA_PATH_V8_0
        $cudnn_version = "7.1.3"
        $cudnn_archive = "cudnn-8.0-windows10-x64-v7.1.zip"
    }
    "9.0" {
        $cuda_path = $Env:CUDA_PATH_V9_0
        $cudnn_version = "7.6.5"
        $cudnn_archive = "cudnn-9.0-windows10-x64-v7.6.5.32.zip"
    }
    "9.1" {
        $cuda_path = $Env:CUDA_PATH_V9_1
        $cudnn_version = "7.1.3"
        $cudnn_archive = "cudnn-9.1-windows10-x64-v7.1.zip"
    }
    "9.2" {
        $cuda_path = $Env:CUDA_PATH_V9_2
        $cudnn_version = "7.6.5"
        $cudnn_archive = "cudnn-9.2-windows10-x64-v7.6.5.32.zip"
    }
    "10.0" {
        $cuda_path = $Env:CUDA_PATH_V10_0
        $cudnn_version = "7.6.5"
        $cudnn_archive = "cudnn-10.0-windows10-x64-v7.6.5.32.zip"
    }
    "10.1" {
        $cuda_path = $Env:CUDA_PATH_V10_1
        $cudnn_version = "8.0.5"
        $cudnn_archive = "cudnn-10.1-windows10-x64-v8.0.5.39.zip"
    }
    "10.2" {
        $cuda_path = $Env:CUDA_PATH_V10_2
        $cudnn_version = "8.0.5"
        $cudnn_archive = "cudnn-10.2-windows10-x64-v8.0.5.39.zip"
    }
    "11.0" {
        $cuda_path = $Env:CUDA_PATH_V11_0
        $cudnn_version = "8.0.5"
        $cudnn_archive = "cudnn-11.0-windows-x64-v8.0.5.39.zip"
    }
    "11.1" {
        $cuda_path = $Env:CUDA_PATH_V11_1
        $cudnn_version = "8.0.5"
        $cudnn_archive = "cudnn-11.1-windows-x64-v8.0.5.39.zip"
    }
    "11.2" {
        $cuda_path = $Env:CUDA_PATH_V11_2
        $cudnn_version = "8.1.0"
        $cudnn_archive = "cudnn-11.2-windows-x64-v8.1.0.77.zip"
    }
    default {
         throw "Unsupported CUDA version: $cuda"
    }
}

$url = "https://developer.download.nvidia.com/compute/redist/cudnn/v${cudnn_version}/${cudnn_archive}"
echo "Downloading ${url}..."
curl.exe -LO "${url}"

install_cudnn $cudnn_archive $cuda_path
