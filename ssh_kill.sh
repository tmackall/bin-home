#!/bin/bash

status=$(kill -9 $(pidof ssh))
mutt mackall.tom@gmail.com -s 'Tunnel kill' < $status
