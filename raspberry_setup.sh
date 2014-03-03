#!/bin/bash

sudo adduser tmackall
sudo adduser tmackall sudo
# raspberry config
# set timezone, disk, over-clock etc
#-----------------------------------------------------------------
sudo raspi-config
# get current os updates
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install vim
sudo apt-get install git
cd /home
sudo mv tmackall tmackall.bck
# add mackall-home etc to this.
sudo vim /etc/hosts 
sudo chmod 777 .
git clone ssh://mackall-home/disk1/github-mackall/homedir.git tmackall
sudo chmod 775 tmackall
sudo chgrp -R tmackall tmackall
sudo chown -R tmackall tmackall
sudo rm -rf tmackall.bck
sudo reboot
cd tmackall
# ssh keys
ssh-keygen -t rsa
scp ~/.ssh/id_dsa.pub <xxxxx>:.ssh/authorized_keys2
git clone ssh://mackall-home/disk1/github-mackall/bin.git bin
sudo apt-get install vim python-dev python-setuptools nginx supervisor
sudo apt-get install python-pip
sudo pip install virtualenv virtualenvwrapper
# install dig for finding DNS entries
sudo apt-get install dnsutils
# ftp server
sudo apt-get install vsftpd
sudo apt-get install sysstat
sudo apt-get install zip
sudo apt-get install vlc
sudo apt-get install tzdata
#
# wifi setup 
#----------------------------------------------------------------------
sudo vim /etc/network/interfaces
# added these lines

allow-hotplug wlan0
auto wlan0
iface wlan0 inet dhcp
wpa-ssid "ssid"
wpa-psk "password"

Go to /etc/ifplugd/action.d/ and rename the ifupdown file to ifupdown.original
Then do: cp /etc/wpa_supplicant/ifupdown.sh ./ifupdown
    Finally: sudo reboot
