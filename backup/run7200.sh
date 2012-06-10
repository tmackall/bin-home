#!/bin/bash
ectool runProcedure "Linux Platform CI" --procedureName  unit_tests --actualParameter ip_addr=129.46.10.153 target_id=7600 target_type=SURF unit_test_dir=/opt/qcom/bin/tests unit_tests_report=unit_tests_report_long.html  --userName admin --password changeme --scheduleName 7200A_SURF

