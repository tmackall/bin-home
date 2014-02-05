#!/bin/bash
netstat -a | grep 12028
sudo fuser -v 12028/tcp
