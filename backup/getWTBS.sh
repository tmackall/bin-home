#!/bin/bash
psql -t -U gerrit2_ro -c "SELECT change_id FROM change_approvals WHERE change_open='Y' AND category_id='CRVW' AND value=2 INTERSECT SELECT change_id FROM change_approvals WHERE category_id='VRIF' AND value=1 EXCEPT ALL SELECT change_id FROM change_approvals WHERE (category_id='VRIF' AND value=-1) OR (category_id='CRVW' AND value=-2)" reviewdb
