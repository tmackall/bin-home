#!/bin/bash
cd ~
for i in `ls`; do du -s $i; done

