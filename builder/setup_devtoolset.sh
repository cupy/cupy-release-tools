#!/bin/bash -uex

if rpm -qa | grep cuda-cudart-11-0; then
    # CentOS 7 (CUDA 11.0)
    yum install -y centos-release-scl
    yum install -y devtoolset-7-gcc-c++
    yum clean all
fi
