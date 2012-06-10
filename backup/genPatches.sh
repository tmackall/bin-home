#!/bin/bash
#
# verify that there are 2 input parameters
echo $#
if [[ "$#" -lt 2 ]]
then echo "Expected getPatches.sh au-01.08.00.ZZZ donut <au-01.08.00.YYY>"
exit 51
fi
refBuild=quic/korg/$2
#
# set the starting point to something other than korg
if [[ "$#" -eq 3 ]]
then refBuild="refs/tags/$3"
fi
echo $refBuild
#
# cd to where the reference build is
cd $TESTHM
cd $2
find . -name "*.patch" | perl -ne 's/^/rm /' -p | tee temp.sh
bash temp.sh
find . -name "base.tag" | perl -ne 's/^/rm /' -p | tee temp.sh
bash temp.sh
#rm -rf $2
#mkdir $2
echo `pwd`
repo init -u git://git-android.quicinc.com/platform/manifest.git -b refs/tags/$1
repo sync

#
# generate the open source patches
export AOSP_PRJS=`repo forall -c \
	'if [ $(git branch -r | grep -q -o 'quic/korg/';\
    echo $?) == 0 ]; then echo "$REPO_PROJECT"; fi' | \
    sed -e 's|kernel/msm||' | xargs`
echo $AOSP_PRJS
repo forall $AOSP_PRJS -c 'git merge-base HEAD $refBuild > base.tag'
repo forall $AOSP_PRJS -c 'git format-patch --no-merges -M `cat base.tag`..HEAD'
#
# generate the qcom-prop source patches
export NON_AOSP_PRJS=`repo forall -c \
	'if [ $(git branch -r | grep -q -o 'quic/korg/';\
    echo $?) != 0 ]; then echo "$REPO_PROJECT"; fi' | \
    grep -v qcom-proprietary | sed -e 's|kernel/msm||' | xargs`
echo $NON_AOSP_PRJS
repo forall $NON_AOSP_PRJS -c 'git format-patch --no-merges --root'
#
# generate the kernel patches
#repo forall kernel/msm -c \
#	'git merge-base HEAD quic/korg/android-msm-2.6.29 > base.tag'
repo forall kernel/msm -c \
	'git merge-base HEAD $refBuild > base.tag'
repo forall kernel/msm -c \
	'git format-patch --no-merges -M `cat base.tag`..HEAD'
#
# tar up the patches
rm -rf  vendor/qcom-patches
mkdir vendor/qcom-patches
find . -iname 0\*.patch -print | tar -c -T - -f - | \
     ( cd vendor/qcom-patches && tar xf -)
tree vendor/qcom-patches | tee vendor/qcom-patches/patch.list
suCmd.exp "rm -rf /prj/lnxbuild/lost_scan/$1" 120
suCmd.exp "mkdir /prj/lnxbuild/lost_scan/$1" 5
cd $TESTHM/$2/vendor/qcom-patches
suCmd.exp "cp -R * /prj/lnxbuild/lost_scan/$1/" 400
tree /prj/lnxbuild/lost_scan/$1/

