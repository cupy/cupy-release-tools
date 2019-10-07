Param(
	[String]$cuda
)

$ErrorActionPreference = "Stop"

function install_cudnn([String]$cudnn_zip, [String]$cuda_root) {
  echo "Installing ${cudnn_zip} to ${cuda_root}..."
  Remove-Item -Recurse -Force -ErrorAction:SilentlyContinue tmp_cudnn
  Expand-Archive -Path ${cudnn_zip} -DestinationPath tmp_cudnn
  Push-Location tmp_cudnn
  Move-Item -Force cuda\bin\* ${cuda_root}\bin
  Move-Item -Force cuda\include\* ${cuda_root}\include
  Move-Item -Force cuda\lib\x64\* ${cuda_root}\lib\x64
  Pop-Location
  Remove-Item -Recurse -Force -ErrorAction:SilentlyContinue tmp_cudnn
}

switch ($cuda) {
    "8.0" {
        $cuda_path = $Env:CUDA_PATH_V8_0
        $cudnn_archive = "cudnn-8.0-windows10-x64-v7.1-ga.zip"
    }
    "9.0" {
        $cuda_path = $Env:CUDA_PATH_V9_0
        $cudnn_archive = "cudnn-9.0-windows10-x64-v7.6.4.38.zip"
    }
    "9.1" {
        $cuda_path = $Env:CUDA_PATH_V9_1
        $cudnn_archive = "cudnn-9.1-windows10-x64-v7.1.zip"
    }
    "9.2" {
        $cuda_path = $Env:CUDA_PATH_V9_2
        $cudnn_archive = "cudnn-9.2-windows10-x64-v7.6.4.38.zip"
    }
    "10.0" {
        $cuda_path = $Env:CUDA_PATH_V10_0
        $cudnn_archive = "cudnn-10.0-windows10-x64-v7.6.4.38.zip"
    }
    "10.1" {
        $cuda_path = $Env:CUDA_PATH_V10_1
        $cudnn_archive = "cudnn-10.1-windows10-x64-v7.6.4.38.zip"
    }
    default {
         throw "Unsupported CUDA version: $cuda"
    }
}


# https://console.cloud.google.com/storage/browser/tmp-asia-pfn-public-ci/cupy-release-tools/cudnn/
gsutil -q -m cp -r gs://tmp-asia-pfn-public-ci/cupy-release-tools/cudnn/$cudnn_archive .

install_cudnn $cudnn_archive $cuda_path
