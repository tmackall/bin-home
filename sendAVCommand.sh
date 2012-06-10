#!/bin/bash
echo -ne $2\\r | nc -w1  $1 23
