#!/bin/bash

echo "Installing required packages..."
sudo groupadd mlocate
sudo apt-get -q -y install git-core gnupg flex bison gperf build-essential zip curl
sudo apt-get -q -y install sun-java6-jdk
sudo apt-get -q -y install ia32-sun-java6-bin
sudo update-java-alternatives -s ia32-java-6-sun
sudo apt-get -q -y install lib32z1-dev gcc-multilib g++-multilib libc6-dev-i386 lib32ncurses5-dev ia32-libs
sudo ln -s /usr/lib32/libX11.so.6 /usr/lib32/libX11.so

mkdir /local/mnt/workspace/lnxbuild 
sudo chown lnxbuild /local/mnt/workspace/lnxbuild
sudo chgrp build_integration /local/mnt/workspace/lnxbuild

echo "Now you need to config samba and select the correct java alternative."
echo "  1. Run sudo update-alternatives --config <cmd> for all <cmd> in"
echo "      java, javah, javac, jar, javadoc"
echo "  2. Run sudo apt-get install samba system-config-samba "
echo "     Then run sudo system-config-samba"
cat <<EOR

Brings up GUI control program.

+ Add Share
   (Basic Tab)
	/local/mnt/workspace/lnxbuild
   + Writable
   + Visible

   (Access Tab)
   + Allow access to anyone
EOR

# TBD: The apt lines above should get everything we need.
#      Verify and cut out the section below.
#sudo apt-get -q -y install git-core gnupg
#sudo apt-get -q -y install sun-java6-jdk
#sudo apt-get -q -y install flex bison gperf libsdl-dev libesd0-dev libwxgtk2.6-dev build-essential zip curl libncurses5-dev
#sudo apt-get -q -y install libc6-dev-i386

echo "Installing the EC agent..."
export EC_INSTALL_TYPE=agent
export AGENT_USER_TO_RUN_AS=lnxbuild
export AGENT_GROUP_TO_RUN_AS=build_integration
cp /prj/lnxbuild/commander/commander_i686_Linux.bin.sh /tmp
sudo /bin/bash /tmp/commander_i686_Linux.bin.sh -q

sudo cp ~zacl/bin/commander.conf /etc/ld.so.conf.d
sudo /sbin/ldconfig

