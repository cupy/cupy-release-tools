#!/bin/bash -uex

PYTHON_VERSIONS=$1
CYTHON_VERSION=$2

if [[ "$(rpm --eval '%{rhel}')" == "7" ]]; then
    # CentOS 7: Use OpenSSL 1.1 for Python 3.10+.
    export CFLAGS="-I/usr/include/openssl11"
    export CPPFLAGS="-I/usr/include/openssl11"
    export LDFLAGS="-L/usr/lib64/openssl11"
fi

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
    pip install -U "Cython==${CYTHON_VERSION}" wheel auditwheel build
done

# The last version installed will be used to run the builder agent.
# pyenv global system
