#!/bin/bash
rm -rf /var/www/reports/AU-reports
cp -rf /prj/lnxbuild/AU-reports /var/www/reports
cp ~/bin/Branch-Table.xsl /var/www/reports/AU-reports
~/bin/createAUTestResults.exp
