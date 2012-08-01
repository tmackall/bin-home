#!/bin/bash
echo -ne $2\\r | nc -w1 -o $3 $1 23
