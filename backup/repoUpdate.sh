#!/bin/bash
curl http://android.git.kernel.org/repo > ~/bin/repo
chmod a+x ~/bin/repo
export PATH=~/bin:$PATH
rm -rf ~/.repoconfig
git config --global user.name "Tom Mackall"
git config --global user.email tmackall@quicinc.com


