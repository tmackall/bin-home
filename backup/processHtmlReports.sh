#!/bin/bash
txt2html /tmp/daily --outfile /tmp/daily.html
mv /tmp/daily.html /var/www/reports/
txt2html /tmp/monthly --outfile /tmp/monthly.html
mv /tmp/monthly.html /var/www/reports/
txt2html /tmp/totals --outfile /tmp/totals.html
mv /tmp/totals.html /var/www/reports/
txt2html /tmp/monthlyTotals --outfile /tmp/monthlyTotals.html
mv /tmp/monthlyTotals.html /var/www/reports/
cat /var/www/reports/monthly.html | perl -ne 's/^(.*Daily totals.*)$/\<FONT COLOR=\"#ff0000\"\>$1\<\/FONT\>/' -p >  /var/www/reports/monthly.html.b
mv /var/www/reports/monthly.html.b /var/www/reports/monthly.html
