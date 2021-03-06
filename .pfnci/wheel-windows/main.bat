:: Example: main.bat 3.7.0 9.0 master

set PYTHON=%1
set CUDA=%2
set BRANCH=%3
set JOB_GROUP=%4

:: Install cuDNN
PowerShell .pfnci\wheel-windows\install_cudnn.ps1 -cuda %CUDA% || exit 1

:: Clone CuPy
git clone --recursive https://github.com/cupy/cupy.git cupy || exit 1
git -C cupy checkout origin/%BRANCH% || exit 1

:: Build
PowerShell .pfnci\wheel-windows\build.ps1 -python %PYTHON% -cuda %CUDA%
set FINAL_STATUS=%errorlevel%

:: Upload wheel to GCS
gsutil -m cp cupy*.whl gs://tmp-asia-pfn-public-ci/cupy-release-tools/build-windows/%JOB_GROUP%_%BRANCH%/%FLEXCI_JOB_ID%_%PYTHON%_%CUDA%/ || exit 1

exit /b %FINAL_STATUS%
