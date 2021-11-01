FROM scratch
ADD _jetson-rootfs.tar /
RUN /bin/sed -i 's|<SOC>|t210|g' /etc/apt/sources.list.d/nvidia-l4t-apt-source.list
CMD /bin/bash
