#!/usr/bin/env bash
sudo qemu-system-arm -kernel kernel-qemu-5.10.63-bullseye \
-cpu arm1176 -m 256 \
-M versatilepb -dtb versatile-pb-bullseye-5.10.63.dtb \
-no-reboot \
-serial stdio \
-append "root=/dev/sda2 panic=1 rootfstype=ext4 rw" \
-hda rpilite.qcow2 \
-net nic -net user \
-net tap,ifname=vnet0,script=no,downscript=no
