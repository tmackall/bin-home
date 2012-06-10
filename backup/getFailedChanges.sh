#!/bin/bash
psql -t -U gerrit2_ro -c "SELECT * FROM patch_set_approvals WHERE category_id='VRIF' AND change_open='Y' AND value < 0" reviewdb
