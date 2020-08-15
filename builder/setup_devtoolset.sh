#!/bin/bash -uex

yum install -y centos-release-scl

if [ $(rpm --eval '%{rhel}') == 6 ]; then
    # CentOS 6
    perl -pi -e 's|^#baseurl=http://mirror.centos.org/centos/6/sclo/\$basearch/rh/|baseurl=http://ftp.iij.ad.jp/pub/linux/centos-vault/6.8/sclo/\$basearch/rh/|' /etc/yum.repos.d/CentOS-SCLo-scl-rh.repo
    perl -pi -e 's|^mirrorlist=|#mirrorlist=|' /etc/yum.repos.d/CentOS-SCLo-scl-rh.repo
    yum install -y devtoolset-6-gcc-c++
else
    # CentOS 7
    yum install -y devtoolset-7-gcc-c++
fi

yum clean all
