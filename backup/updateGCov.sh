#!/bin/bash
rm -rf /var/www/reports/code_coverage/*
cp -rp /prj/lnxbuild/code_coverage/coverage* /var/www/reports/code_coverage
cp ~/bin/CC.xsl /var/www/reports/code_coverage
~/bin/createKCov.exp
