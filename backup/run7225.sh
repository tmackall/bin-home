#!/bin/bash
echo 'ectool runProcedure "Linux Platform CI" --procedureName  unit_tests --actualParameter ip_addr=129.46.10.153 target_id=7625 target_type=SURF unit_test_dir=/opt/qcom/bin/tests unit_tests_report=unit_tests_report_7225.html  --userName admin --password changeme'
ectool login admin changeme
ectool runProcedure "Linux Platform CI" --procedureName unit_tests --actualParameter ip_addr=129.46.10.153 target_id=7625 target_type=SURF unit_test_dir=/opt/qcom/bin/tests unit_tests_report=unit_tests_report_7225.html --userName admin --password changeme

