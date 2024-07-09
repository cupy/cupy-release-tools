#!/bin/bash -uex

sed -i -E -e 's|^mirrorlist=|#mirrorlist=|g' /etc/yum.repos.d/*.repo
sed -i -E -e 's|^#( ?)baseurl=http://mirror.centos.org/centos/(7\|\$releasever)/|baseurl=http://ftp.jaist.ac.jp/pub/Linux/CentOS-vault/7.9.2009/|g' /etc/yum.repos.d/*.repo
sed -i -E -e 's|^#( ?)baseurl=http://download.fedoraproject.org/pub/epel/7/|baseurl=http://ftp.jaist.ac.jp/pub/Linux/Fedora/epel/7/|g' /etc/yum.repos.d/*.repo
