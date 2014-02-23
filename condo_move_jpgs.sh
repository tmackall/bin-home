#!/bin/bash

pushd ~/ftp
scp *.jpg mackall-home:ftp/ps02
rm -rf ~/ftp/*.jpg
popd
