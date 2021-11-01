#!/bin/bash

# This script requires sudo privilage, and assumes parted (partprobe) installed.
# Note: this process cannot be containerized as `partprobe` relies on udev.

set -uex

sudo echo "Checking sudo privilage"

if [ ! -f sd-blob-b01.img ]; then
    if [ ! -f image.zip ]; then
        wget -q -O image.zip "https://developer.nvidia.com/embedded/l4t/r32_release_v6.1/jeston_nano/jetson-nano-jp46-sd-card-image.zip"
    fi
    unzip image.zip
fi

LOOP_DEV=$(sudo losetup --show -f sd-blob-b01.img)
trap "sudo umount ${LOOP_DEV}p1; sudo losetup -d ${LOOP_DEV}" EXIT
sudo partprobe "${LOOP_DEV}"
mkdir -p _jetson-rootfs
sudo mount -o ro "${LOOP_DEV}p1" _jetson-rootfs
sudo tar cf _jetson-rootfs.tar -C _jetson-rootfs .

sudo docker run --rm --privileged multiarch/qemu-user-static --reset -p yes
sudo docker build -t asia.gcr.io/pfn-public-ci/cupy-release-tools:cuda-10.2-jetson .
echo "Done. Maintainers can push the Docker image by:"
echo "$ docker push asia.gcr.io/pfn-public-ci/cupy-release-tools:cuda-10.2-jetson"
