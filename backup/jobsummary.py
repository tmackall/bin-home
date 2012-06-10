#!/usr/bin/env python
#-----------------------------------------------------------------------------
# Copyright (c) 2011 QUALCOMM Incorporated.
# All Rights Reserved. QUALCOMM Proprietary and Confidential.
#-----------------------------------------------------------------------------
# jobsummary - script to print test result counts for a Commander job
# Usage: jobsummary <job_number>
# Copies test_from_linux_task*.log from
# /prj/lnxbuild/workspaces/*_<job_number> to $HOME/logs/<job_number>
# and prints combined result counts for those logs
#-----------------------------------------------------------------------------

import glob
import os
import re
import sys

class Results(object):
    def __init__(self):
        self.test_runs = [ ]

    def status(self, test_name):
        for test_run in self.test_runs:
            if test_name in test_run.results.keys():
                if test_name in test_run.nbfailed:
                    status= 'non-blocking fail'
                else:
                    status= test_run.results[test_name]
                reason = test_run.reasons[test_name]
                return "status:%s with reason: %s " % (status, reason)
        return 'unexecuted'

    def test_list(self):
        test_names = set()
        for test_run in self.test_runs:
            for test_name in test_run.results.keys():
                test_names.add(test_name)
        return ' '.join(sorted(test_names))

    def dump_simple(self):
        simple_results = [ ]
        for test_run in self.test_runs:
            for test_name in test_run.results.keys():
                if test_name in test_run.nbfailed:
                    status = 'non-blocking fail'
                else:
                    status = test_run.results[test_name]
                simple_results.append('%s - %s - %s' % (test_name, status, test_run.reasons[test_name]))
        for result in sorted(simple_results):
            print result

    def dump(self):
        """ Print test counts to stdout"""
        counts = { }
        overall_counts = { }
        target_counts = { }
        branch_counts = { }
        fail_counts_by_target = { }
        nbfail_counts_by_target = { }
        test_run_pass_counts = { }
        test_run_counts = { }
        fail_jobs_by_target  = { } # [target][failure]
        nbfail_jobs_by_target  = { } # [target][failure]
        pass_jobs_by_target  = { } # [target][test]
        fail_details_by_target = { }

        for test_run in self.test_runs:
            target = test_run.target()
            target_counts[target] = target_counts.setdefault(target, 0) + 1
            test_run_counts[target] = test_run_counts.setdefault(target, 0) + 1
            test_run_pass_counts.setdefault(target, 0)
            fail_jobs_by_target.setdefault(target, { })
            nbfail_jobs_by_target.setdefault(target, { })
            pass_jobs_by_target.setdefault(target, { })
            fail_details_by_target.setdefault(target, { })

            branch = test_run.branch
            branch_counts[branch] = branch_counts.setdefault(branch, 0) + 1

            test_run_passed = True
            for test_name in sorted(test_run.results.keys()):
                status = test_run.results[test_name]
                counts_for_test = counts.setdefault(test_name, { })
                counts_for_test[status] = counts_for_test.setdefault(status, 0) + 1
                overall_counts[status] = overall_counts.setdefault(status, 0) + 1
                if status == 'passed':
                    pass_jobs = pass_jobs_by_target[target]
                    pass_jobs.setdefault(test_name, set()).add(test_run.job_number)
                    if test_name in test_run.nbfailed:
                        nbfail_key = '%s - %s' % (test_name, test_run.nbfailed[test_name])
                        nbfail_counts = nbfail_counts_by_target.setdefault(target, { })
                        nbfail_counts[nbfail_key] = nbfail_counts.setdefault(nbfail_key, 0) + 1
                        nbfail_jobs = nbfail_jobs_by_target[target]
                        nbfail_jobs.setdefault(nbfail_key, set()).add(test_run.job_number)
                else:
                    test_run_passed = False
                    fail_key = '%s - %s' % (test_name, test_run.reasons[test_name])
                    fail_counts = fail_counts_by_target.setdefault(target, { })
                    fail_counts[fail_key] = fail_counts.setdefault(fail_key, 0) + 1
                    fail_details = fail_details_by_target[target].setdefault(fail_key, set())
                    fail_jobs = fail_jobs_by_target[target]
                    fail_jobs.setdefault(fail_key, set()).add(test_run.job_number)
                    if test_name in test_run.test_output:
                        fail_details.add(test_run.test_output[test_name])
            if test_run_passed:
                test_run_pass_counts[target] = test_run_pass_counts[target] + 1

        print 'Result counts:'
        for status in sorted(overall_counts.keys()):
            print '  %4d %s' % (overall_counts[status], status.title())

        print '\nPass rate:'
        for test_name in sorted(counts):
            pass_count = 0
            total_count = 0

            for status in counts[test_name]:
                count = counts[test_name][status]
                total_count = total_count + count
                if status == 'passed':
                    pass_count = count
            if total_count > 0:
                print '  %6.2f%%' % (float(pass_count) * 100 / total_count),
            print '%s - %d/%d' % (test_name, pass_count, total_count)

        print '\nTest runs: %d' % len(self.test_runs)
        print ' ', '\n  '.join(sorted(branch_counts.keys()))
        for target in sorted(target_counts.keys()):
            print '  %5s %s ' % ('%d/%d' % (test_run_pass_counts[target], test_run_counts[target]), target)

        if len(nbfail_counts_by_target):
            print '\nNon-blocking failures:'
            print
            for target in sorted(nbfail_counts_by_target.keys()):
                print target
                nbfail_counts = nbfail_counts_by_target[target]
                for nbfailure in sorted(nbfail_counts.keys()):
                    print '  %3d - %s' % (nbfail_counts[nbfailure], nbfailure)
                    print '        ->failed in jobs', ', '.join(sorted(nbfail_jobs_by_target[target][nbfailure]))
        if len(fail_counts_by_target):
            fails_out = file('fail_details.txt', 'w')
            print '\nFailures:'
            print
            fails_out.write('Failures:\n\n')
            for target in sorted(fail_counts_by_target.keys()):
                print target
                fails_out.write('[%s]\n' % target)
                fail_counts = fail_counts_by_target[target]
                for failure in sorted(fail_counts.keys()):
                    print '  %3d - %s' % (fail_counts[failure], failure)
                    print '        ->Failed in jobs', ', '.join(sorted(fail_jobs_by_target[target][failure]))
                    test_name = re.sub(r' - .*', '', failure)
                    if target in pass_jobs_by_target and test_name in pass_jobs_by_target[target]:
                        print '        ->Passed in jobs', ', '.join(sorted(pass_jobs_by_target[target][test_name]))
                    fails_out.write('\n\n***************************************************************************\n')
                    fails_out.write('    The issue: %s\n'% (failure))
                    fails_out.write('    occurred %d times\n' % (fail_counts[failure]))
                    fails_out.write('***************************************************************************\n')
                    for n, fail_details in enumerate(sorted(fail_details_by_target[target][failure])):
                        fails_out.write('***************************************************************************\n')
                        fails_out.write('    Details variant #%d \n' % (n+1))
                        fails_out.write('***************************************************************************\n')
                        fails_out.write('%s\n' % (fail_details[:3000]))
                        if len(fail_details) > 3000 :
                            fails_out.write('***************************************************************************\n')
                            fails_out.write('!!!!!!!  Actual details truncated, see .log files for full details  !!!!!!!\n')
                            fails_out.write('***************************************************************************\n')

            print '(Failure details written to fail_details.txt)\n'

class TestRun(object):
    def __init__(self):
        self.results = { }
        self.reasons = { }
        self.nbfailed = { }
        self.test_product = 'unknown-test_product'
        self.branch = 'unknown-branch'
        self.target_host = 'unknown-host'
        self.job_number = 'unknown-job'
        self.test_output = { }

    def target(self):
        return '%s %s (%s)' % (self.test_product, self.target_host, self.actual_hardware)

    def result(self, test_name, status, reason=None):
        if status == 'nb-failed':
            self.nbfailed[test_name] = reason
            status = 'passed'
        self.results[test_name] = status
        if status != 'passed':
            if reason is None:
                reason = '(%s)' % status
            self.reasons[test_name] = reason

class LogParser(object):
    def __init__(self):
        self.test_runs = [ ]

    def parse(self, log_path, test_runs):
        print 'Parsing', log_path
        self.test_runs = test_runs
        self.current_run = None
        self.current_actual_hardware = None
        self.reset_test_state()

        log = open(log_path)
        for line in log:
            line = line.rstrip()
            if self.looking_for != None and line == self.looking_for:
                self.in_execution = True
                self.looking_for = None
            # CRF|20:11:48|TEST CASE START: fstest_tc0010
            if line.find('Executing suiteStart proc for suite') > -1:
                self.test_output[:] = [ line ]
                self.in_execution = True
            else:
                m = re.search(r'^CRF\|(\d+:\d+:\d+)\|([^:]+):?\s*(.*)$', line)
                if m:
                    timestamp = m.group(1)
                    event = m.group(2)
                    details = m.group(3)
                    self.handle(timestamp, event, details)
                elif line.find('failed to execute all the tests') > -1:
                    print '    Failed test run:', self.pending_reason
                elif self.in_execution:
                    if re.search(r'(^\d{8,}@|\$ )', line):
                        self.in_execution = False
                    else:
                        self.test_output.append(line)
                else:
                    m = re.search(r'FAIL:.*:([^,more ]+),.*--> test (returned \d+)', line)
                    if m:
                        self.current_run.reasons[self.current_test] = '%s %s' % (m.group(1), m.group(2))
                    
                    m = re.search(r'spawn /usr/bin/ssh.* (\S+)', line)
                    if m:
                        self.current_run.target_host = m.group(1)

                    m = re.search(r'ACTUAL_HARDWARE is now (.*)', line)
                    if m:
                        self.current_actual_hardware = m.group(1)

                    m = re.search(r'JOBID is now (.*)', line)
                    if m:
                        self.job_number = m.group(1)

        # Don't punish last test if had a partial log file
        if self.current_run and self.current_test in self.current_run.results and self.pending_reason is None:
            del self.current_run.results[self.current_test]

    def reset_test_state(self):
        self.current_test = 'unknown'
        self.pending_reason = None
        self.job_number = 'unknown'
        self.test_output = [ ]
        self.in_execution = False
        self.looking_for = None

    def product_for_target(self, target):
        targets_by_product = {
            'msm7627_surf' : [
                'msm7627_ffa',
            ],
            'msm7630_surf' : [
                'msm7630_ffa',
                'msm8655_ffa',
                'msm8655_surf',
            ],
            'msm8660_surf' : [
                'msm8660_ffa',
                'msm8660_fluid',
            ],
        }
        for product in targets_by_product:
            for product_target in targets_by_product[product]:
                if product_target == target:
                    return product
        return target
        
    def handle(self, timestamp, event, details):
        if event == 'CRF INIT':
            self.current_run = TestRun()
            self.current_run.job_number = self.job_number
            self.test_runs.append(self.current_run)
        elif event == 'BRANCH':
            self.current_run.branch = details
        elif event == 'TARGET':
            self.current_run.actual_hardware = details
            self.current_run.test_product = self.product_for_target(details)
        elif event == 'TEST CASE START':
            self.current_test = details
            self.current_run.result(self.current_test, 'unresolved', '')
        elif event == 'TEST CASE END':
            test_name = details
            if self.current_test == 'unknown':
                if 'unknown' in self.current_run.results:
                    result = self.current_run.results['unknown']
                    del self.current_run.results['unknown']
                    if 'unknown' in self.current_run.reasons:
                        reason = self.current_run.reasons['unknown']
                        del self.current_run.reasons['unknown']
                    else:
                        reason = None
                    self.current_run.result(test_name, result, reason)
                    self.current_test = test_name
                else:
                    self.current_run.result(test_name, 'unresolved', self.pending_reason)
            if test_name not in self.current_run.results or self.current_run.results[test_name] == 'unresolved':
                print '->No result for', test_name
            if self.pending_reason:
                self.current_run.reasons[test_name] = self.pending_reason
            self.current_run.test_output[test_name] = \
                re.sub(r'CRF\|\d\d:\d\d:\d\d', 'CRF|HH:MM:SS', '\n'.join(self.test_output))
            self.reset_test_state()
        elif event == 'PASS':
            have_name = re.search(r'^([^:]+):.* passed$', details)
            if have_name:
                self.current_test = have_name.group(1)
            self.current_run.result(self.current_test, 'passed', '')
        elif event == 'FAIL':
            have_name = re.search(r'^([^:]+):.* failed$', details)
            if have_name:
                self.current_test = have_name.group(1)
            self.current_run.result(self.current_test, 'failed', details)
        elif event == 'Executing now':
            self.test_output[:] = [ ]
            self.looking_for = details
        elif event == 'NON BLOCKING FAIL':
            m = re.search(r'^(.*):', details)
            if m:
                self.handle(timestamp, 'TEST CASE START', m.group(1))
                self.current_run.result(self.current_test, 'nb-failed', details[m.end():])
        elif event == 'ERROR':
            self.pending_reason = details

class LogSet(object):
    def __init__(self, archive_root, logs_dir):
        self.results = Results()
        self.archive_root = archive_root
        self.logs_dir = logs_dir

    def add_job(self, job_number):
        workspace_dirs = glob.glob('%s/workspaces/*_%s' % (self.archive_root, job_number))
        if len(workspace_dirs) == 0:
            workspace_dirs = glob.glob('%s/workspaces/*_%s_*' % (self.archive_root, job_number))

        if len(workspace_dirs) == 0:
            workspace_dirs = glob.glob('%s/workspaces_test/*_%s' % (self.archive_root, job_number))

        if len(workspace_dirs) == 0:
            workspace_dirs = glob.glob('%s/workspaces_test/*_%s_*' % (self.archive_root, job_number))

        if len(workspace_dirs) == 0 or not os.path.exists(workspace_dirs[0]):
            usage('No commander workspace for job_number=%s' % job_number)

        print 'Results for Job %s' % job_number
        workspace_dir = workspace_dirs[0]
        
        try:
            os.chdir(self.logs_dir)
            if not os.path.exists('logs'):
                os.mkdir('logs')
            os.chdir('logs')
            if not os.path.exists(job_number):
                os.mkdir(job_number)
            print 'Copying logs from %s' % workspace_dir
            os.system('cp %s/test_from_linux_task*.log %s' % (workspace_dir, job_number))
            os.chdir(job_number)
        except:
            os.chdir(workspace_dir)
            
        self.log_dir = os.getcwd()
        self.logs = glob.glob('test_from_linux_task*.log')
        for log in self.logs:
            self.parse_log(log)

    def dump_summary(self, simple_format = False):
        print
        if simple_format:
            self.results.dump_simple()
        else:
            self.results.dump()

    def parse_log(self, log_path):
        LogParser().parse(log_path, self.results.test_runs)

def usage(error=None):
    if error:
        sys.stderr.write('Error: %s\n' % error)
    sys.stderr.write('Usage: jobsummary <job_number or log file> [<more job numbers/log files>]\n')
    sys.stderr.write('Copies test_from_linux_task*.log from\n')
    sys.stderr.write('/prj/lnxbuild/workspaces/*_<job_number> to $HOME/logs/<job_number>\n')
    sys.stderr.write('and prints combined result counts for those logs\n')
    sys.exit(1)

class JobSummary(object):
    def __init__(self, archive_root = '/prj/lnxbuild', logs_dir = '/local/mnt/workspace'):
        self.logs = LogSet(archive_root, logs_dir)

    def parse(self, item):
        if os.path.exists(item) and os.path.isfile(item):
            self.logs.parse_log(item)
        else:
            self.logs.add_job(item)

    def summary(self, simple_format = False):
        self.logs.dump_summary(simple_format)

    def status(self, test_name):
        return self.logs.results.status(test_name)

    def test_list(self):
        return self.logs.results.test_list()

def process(*items):
    summary = JobSummary()
    simple_format = False
    for item in items:
        if re.match('--simple', item):
            simple_format = True
        else:
            summary.parse(item)
    summary.summary(simple_format)

def main():
    args = sys.argv[1:]
    if len(args) == 0 or re.match(r'-h|--help', args[0]):
        usage()

    process(*args)
    sys.exit(0)

if __name__ == '__main__':
    main()
