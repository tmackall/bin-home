#!/bin/bash
# reboot the 3com switch first
snmpset -v 2c -c private pps1 outlet6Command.0 i 3
