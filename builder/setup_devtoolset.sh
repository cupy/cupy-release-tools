#!/bin/bash -uex

yum install -y centos-release-scl

# CentOS 7
yum install -y devtoolset-7-gcc-c++

yum clean all
