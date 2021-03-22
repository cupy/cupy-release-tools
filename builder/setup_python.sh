#!/bin/bash -uex

PYTHON_VERSIONS=$1
CYTHON_VERSION=$2

# Install OpenSSL for CentOS 6; Python 3.7 requires OpenSSL 1.0.2 or 1.1
# compatible libssl with X509_VERIFY_PARAM_set1_host, whereas CentOS 6 provides
# 0.9.8 and 1.0.1.
if [ $(rpm --eval '%{rhel}') == 6 ]; then
    OPENSSL_ROOT=openssl-1.0.2o
    OPENSSL_FILE=${OPENSSL_ROOT}.tar.gz
    OPENSSL_HASH=ec3f5c9714ba0fd45cb4e087301eb1336c317e0d20b575a125050470e8089e4d
    curl -s -q -o "${OPENSSL_FILE}" "https://www.openssl.org/source/${OPENSSL_FILE}"
    echo "${OPENSSL_HASH}  ${OPENSSL_FILE}" | sha256sum -cw --quiet -
    tar xf "${OPENSSL_FILE}"
    pushd "${OPENSSL_ROOT}"
    ./config no-ssl2 no-shared -fPIC --prefix=/usr/local/ssl &> /tmp/openssl-config.log
    make &> /tmp/openssl-make.log
    make install_sw &> /tmp/openssl-make-install_sw.log
    popd
    rm -rf "${OPENSSL_ROOT}" "${OPENSSL_ROOT}.tar.gz"

    export CFLAGS=-I/usr/local/ssl/include
    export LDFLAGS=-L/usr/local/ssl/lib
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
    pip install "Cython==${CYTHON_VERSION}" wheel auditwheel
done

# The last version installed will be used to run the builder agent.
# pyenv global system
