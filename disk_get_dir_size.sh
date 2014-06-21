#!/bin/bash
if [[ $# -eq 1 ]]; then
    pushd "$1"
fi
for i in `ls`; do du -s $i; done
popd

