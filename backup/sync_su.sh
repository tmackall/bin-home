#!/bin/bash 

p4 sync @VU_PLATFORM_LINUX_BOOT.$1,@VU_PLATFORM_LINUX_BOOT.$1 &
p4 sync @VU_PLATFORM_LINUX_BUILD.$1,@VU_PLATFORM_LINUX_BUILD.$1 &
p4 sync @VU_PLATFORM_LINUX_COMMON.$1,@VU_PLATFORM_LINUX_COMMON.$1 &
p4 sync @VU_PLATFORM_LINUX_MODULES.$1,@VU_PLATFORM_LINUX_MODULES.$1 &
p4 sync @VU_PLATFORM_LINUX_ROOTFS.$1,@VU_PLATFORM_LINUX_ROOTFS.$1 &
p4 sync @VU_PLATFORM_LINUX_TESTS.$1,@VU_PLATFORM_LINUX_TESTS.$1 &
