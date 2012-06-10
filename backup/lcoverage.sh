##!/bin/bash
#args=("$@")
start=`date`
echo $start
cd $HOME/lcov
rm -rf reports
mkdir reports
cd reports
cp /prj/happyfeet/users/tmackall/coverageData.tar .
tar -xvf coverageData.tar
lcov -d . -c -t kernel_tests -o kernelCoverage.info
gendesc -o kernelOutput kernelCoverage.info
genhtml -s -t "Kernel Unit Tests" -d kernelOutput -o kernel_coverage_data kernelCoverage.info

