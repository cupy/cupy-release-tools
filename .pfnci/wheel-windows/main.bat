:: Example: main.bat 3.7.0 9.0 origin/master

set PYTHON=%1
set CUDA=%2
set BRANCH=%3

:: Install cuDNN
PowerShell .pfnci\wheel-windows\install_cudnn.ps1 -cuda %CUDA%

:: Clone CuPy
git clone https://github.com/cupy/cupy.git cupy
git -C cupy checkout %BRANCH%

:: Build
PowerShell .pfnci\wheel-windows\build.ps1 -python %PYTHON% -cuda %CUDA%

:: Upload wheel to GCS
gsutil -m cp cupy*.whl gs://tmp-asia-pfn-public-ci/cupy-release-tools/build-windows/%FLEXCI_JOB_ID%_%PYTHON%_%CUDA%/
