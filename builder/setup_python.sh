#!/bin/bash -uex

PYTHON_VERSIONS=$1

# Explicitly override "LDFLAGS" set in ROCm docker images.
export LDFLAGS=""

# Install Python
for VERSION in ${PYTHON_VERSIONS}; do
    pyenv install ${VERSION} &
done
wait

# Install Python libraries.
for VERSION in ${PYTHON_VERSIONS}; do \
    echo "Installing libraries on Python ${VERSION}..."
    pyenv global ${VERSION}
    pip install -U pip setuptools
    pip install -U -r requirements.cupy-build.txt wheel auditwheel build
done

# The last version installed will be used to run the builder agent.
# pyenv global system
