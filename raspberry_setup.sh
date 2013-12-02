#!/bin/bash

sudo adduser tmackall
sudo adduser tmackall sudo
ssh-keygen -t dsa
sudo apt-get install vim
ssh-keygen -t dsa
scp ~/.ssh/id_dsa.pub <xxxxx>:.ssh/authorized_keys2
