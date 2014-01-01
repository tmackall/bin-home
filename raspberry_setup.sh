#!/bin/bash

sudo adduser tmackall
sudo adduser tmackall sudo
# raspberry config
sudo raspi-config
# timezone
sudo dpkg-reconfigure tzdata
ssh-keygen -t dsa
sudo apt-get install vim
ssh-keygen -t dsa
scp ~/.ssh/id_dsa.pub <xxxxx>:.ssh/authorized_keys2
sudo apt-get install git
cd /home
sudo mv tmackall tmackall.bck
sudo chmod 777 .
git clone ssh://mackall-home/disk1/github-mackall/homedir.git tmackall
sudo chmod 775 tmackall
cd tmackall
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
