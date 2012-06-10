#!/bin/bash
args=("$@")
start=`date`
echo $start
umask 022
#echo arguments to the shell
tip=0
P4C="xxxx"
buildFlags=""
USAGE="usage: ./doBuild.sh -t -f GCOV=2 -c tmackall_linux-7225"
if [ $# = 0 ]
   then
   	echo "$USAGE"
   	return 1
fi
while getopts "c:f:t" optionName; 
do case $optionName in
   t) tip=1;;
   c) echo "c.....";P4C="$OPTARG";;
   f) buildFlags="$OPTARG";;
   *) echo $USAGE; return 1;;
   esac
done
shift $(($OPTIND - 1))
if [ "$P4C" = "xxxx" ]
   then
   	echo "$USAGE 2"
   	return 1
fi
export P4CLIENT=$P4C
client=$P4C
#buildFlags=${args[1]}
echo $buildFlags
echo $client
echo $tip
#exit 1
delc ${client}
cd /local/mnt/workspace/tmackall/
rm -rf $client
cat ~/bin/template.cs | perl -ne s/tmackall_linux-template/${client}/g -p | tee ~/bin/temp.cs
p4 client -i < ~/bin/temp.cs
target=${client/*-/}
echo $target
case "$target" in
	'7200') label=LINUX_PLATFORM_7200A_SURF_TIP;export TARGET_ID=7200;
	export BUILD=SDCAALBM;export ASIC=7200J;;
	'1105') label=LINUX_PLATFORM_1105_SURF_TIP;export TARGET_ID=1105;
	export BUILD=SNCAALCM;export ASIC=1105A;;
	'7225') label=LINUX_PLATFORM_7625_SURF_TIP;export TARGET_ID=7625;
	export BUILD=SNCAALBM;export ASIC=7625A;;
	'8650') label=LINUX_PLATFORM_8650_SURF_TIP;export TARGET_ID=8650;
	export BUILD=SDCAALBM;export ASIC=8650A;;
	*) echo "no match";return 1;;

esac
if [ "$tip" = "1" ]
then
   echo "sync to the tip"
   p4 sync
else
   echo "sync to the label"
   p4 sync @${label}
fi
cd /local/mnt/workspace/tmackall/$client/LINUX/build
echo "make untar_modem"
make untar_modem
# make the build for apps now
export BUILD=${BUILD//%M/A} 
echo "make -j 4"
make -j 4 $buildFlags
make tests -j 4 $buildFlags
echo "make tests"
echo "Built the ${target} target"
echo "start: ${start}"
echo "end:   `date`"

