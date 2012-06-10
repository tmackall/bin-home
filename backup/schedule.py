#!/usr/bin/env python2.6
#

import datetime
from optparse import OptionParser
import os
import re
from suds.client import Client
import sys

story_points_field = 'customfield_10001'
blocked_field = 'customfield_10063'
md_escapes = re.compile("([%s])" % re.escape("\`*_{}[]()#+-.!"))

def md_escape_repl (matchobj):
  return "\\%s" % matchobj.group(0)

def put_issues_in_sprints (issues, velocities, ignore_id=None, schedule_linearly=False):
  user_sprints = {}
  user_sprints_finished = {}
  to_be_unscheduled = []
  for user, velocity in velocities.iteritems():
    user_sprints[user] = []
    user_sprints_finished[user] = []

  for issue in issues:
    scheduled = 0
    points = 0
    assignee = issue.assignee
    key = issue.key
    if ignore_id and issue.fixVersions and ignore_id == issue.fixVersions[0].id:
      continue
    if not issue.fixVersions:
      issue.fixVersions = [soapclient.factory.create('tns1:RemoteVersion')]
      issue.fixVersions[0].name = "Unscheduled"
    customFields = issue.customFieldValues
    for c in customFields:
      if c.customfieldId == blocked_field:
        # Don't schedule blocked items
        to_be_unscheduled.append(key)
        break
      elif c.customfieldId == story_points_field:
        points = int(c.values[0]);

    if key in to_be_unscheduled:
      continue

    if assignee in user_sprints:
      sprints = user_sprints[assignee]
    else:
      print "WARNING: unknown user %s for issue %s" % (assignee, key)
      continue

    for sprint in sprints:
      if sprint in user_sprints_finished[assignee]:
        continue
      elif (sprint[0] + points) > velocities[assignee]:
        if schedule_linearly:
          user_sprints_finished[assignee].append(sprint)
        continue
      else:
        sprint[0] = sprint[0] + points
        sprint[1].append((key, assignee, issue.summary, issue.fixVersions[0].name))
        scheduled = 1
        break

    if not scheduled:
      sprints.append([points, [(key, assignee, issue.summary, issue.fixVersions[0].name),]])

  return user_sprints, to_be_unscheduled

def merge_user_sprints (user_sprints):
  master_sprints = []
  for user, sprints in user_sprints.iteritems():
    for i in range(len(sprints)):
      if len(master_sprints) > i:
        master_sprints[i][0] += sprints[i][0]
        master_sprints[i][1].extend(sprints[i][1])
      else:
        master_sprints.append(sprints[i])
  return master_sprints

def adjust_velocity_for_recurring_issues(velocities, issues):
  for issue in issues:
    customFields = issue.customFieldValues
    for c in customFields:
      if c.customfieldId == story_points_field:
        points = int(c.values[0]);
    print "(%s, %s, %s)" % (issue.key, issue.assignee, issue.summary)
    velocities[issue.assignee] = velocities[issue.assignee] - points
    if velocities[issue.assignee] <= 0:
      print "WARNING: %s has more recurring tasks than can be completed with the configured velocity." % issue.assignee

def update_subtasks(soapclient, auth, key, version):
  subtask_query = "parent = %s and Status in (new, open, reopened, \"in progress\")" % key
  subtask_issues = soapclient.service.getIssuesFromJqlSearch(auth, subtask_query, 10000)
  if version:
    _version=[version]
  else:
    _version=[]
  for issue in subtask_issues:
    soapclient.service.updateIssue(auth, issue.key, [{"id": "fixVersions", "values": _version }])


if __name__ == '__main__':
  usage = "usage: %prog <required options>"
  parser = OptionParser(usage=usage)
  parser.add_option("--ignore-first-sprint", action="store_true", dest="ignore_first_sprint", default=False)
  parser.add_option("--update-first-sprint", action="store_false", dest="ignore_first_sprint")
  parser.add_option("--dry-run", action="store_true", dest="dry_run", default=False)
  parser.add_option("--server", dest="server", default="jira-tst.qualcomm.com")
  parser.add_option("--auth", dest="authFile", default="/usr2/tmackall/jirabait")
  parser.add_option("--config", dest="config", default=".workflow_config")
  parser.add_option("--show-changes", action="store_true", dest="show_changes", default=False)
  (options, args) = parser.parse_args()

  ignore_first_sprint=options.ignore_first_sprint
  dry_run=options.dry_run

  jira_url = 'https://' + options.server + '/jira/rpc/soap/jirasoapservice-v2?wsdl'
  jira_issue_url = 'https://' + options.server + '/jira/browse'
  authFile = options.authFile

  # Reading component specific variables from the config file
  #  project_name
  #  component_name
  #  schedule_linearly
  #  sprint_prefix
  #  sprint_weeks
  #  velocities
  execfile(options.config)

  real_sprint_days = int(sprint_days/5)*7 + int(sprint_days%5)
  sprint_duration = datetime.timedelta(days=real_sprint_days)

  try:
    f = open(authFile)
    user = f.readline()
    user = user.rstrip()
    passwd = f.readline()
    passwd = passwd.rstrip()
  except ValueError:
    print "ERROR: Invalid authentication file."
    exit(1)

  soapclient = Client(jira_url)
  auth = soapclient.service.login(user, passwd)

  soap_query = ("""project = "%s" and issuetype = "Story" and labels = "overhead" and """
    """Component = "%s" and Status in (new, open, reopened, "in progress") order by "Backlog Rank" """) % (project_name, component_name)
  issues = soapclient.service.getIssuesFromJqlSearch(auth, soap_query, 10000)
  print "Processing overhead tasks:"
  adjust_velocity_for_recurring_issues(velocities, issues)

  soap_query = ('project = "%s" and issuetype = "Story" and "Story Points" > 0 and (labels != "overhead" or labels != "sceduler_ignoreme" or labels is EMPTY) and '
    'Component = "%s" and Status in (new, open, reopened, "in progress") order by "Backlog Rank" ') % (project_name, component_name)
  issues = soapclient.service.getIssuesFromJqlSearch(auth, soap_query, 10000)

  versions = soapclient.service.getVersions(auth, project_name)
  workflow_versions = []
  unreleased_workflow_versions = []
  for i in range(len(versions)):
    if re.match(sprint_prefix, versions[i].name):
      workflow_versions.append(versions[i])
      if not versions[i].released:
        unreleased_workflow_versions.append(versions[i])
  workflow_versions.sort(cmp=lambda x,y: cmp(x.releaseDate, y.releaseDate))
  unreleased_workflow_versions.sort(cmp=lambda x,y: cmp(x.releaseDate, y.releaseDate))

  next_workflow_release_date = workflow_versions[len(workflow_versions)-1].releaseDate + sprint_duration
  # If we land on a weekend we need to extend the sprint to end on a business day.
  if next_workflow_release_date.weekday() >= 5:
    next_workflow_release_date = next_workflow_release_date + datetime.timedelta(days=2)

  if ignore_first_sprint:
    ignore_id = unreleased_workflow_versions[0].id
  else:
    ignore_id = None

  user_sprints, to_be_unscheduled  = put_issues_in_sprints(issues, velocities, ignore_id, schedule_linearly)
  print "INFO: %d BLOCKED Stories\n" % len(to_be_unscheduled)
  for key in to_be_unscheduled:
    if not dry_run:
      soapclient.service.updateIssue(auth, key, [{"id": "fixVersions", "values": [] }])
      update_subtasks(soapclient, auth, key, None)

  master_sprints = merge_user_sprints(user_sprints)

  if ignore_first_sprint:
    unreleased_workflow_versions.pop(0)

  for i in range(len(master_sprints)):
    if i > len(unreleased_workflow_versions)-1:
      if not dry_run and len(unreleased_workflow_versions) < sprints_to_schedule:
        new_version = soapclient.service.addVersion(auth, project_name, {'name':"%s %d" % (sprint_prefix, len(workflow_versions)), 'releaseDate':next_workflow_release_date})
      else:
        new_version=soapclient.factory.create('tns1:RemoteVersion')
        new_version.name = "%s %d" % (sprint_prefix, len(workflow_versions))
        new_version.releaseDate = next_workflow_release_date
      unreleased_workflow_versions.append(new_version)
      workflow_versions.append(new_version)
      next_workflow_release_date = next_workflow_release_date + sprint_duration
      if next_workflow_release_date.weekday() >= 5:
        next_workflow_release_date = next_workflow_release_date + datetime.timedelta(days=2)
    if i < len(unreleased_workflow_versions):
      print "## %s" % unreleased_workflow_versions[i].name
      print "### Release Date %s" % unreleased_workflow_versions[i].releaseDate.date()
    for info in master_sprints[i][1]:
      md_friendly_summary = md_escapes.sub(md_escape_repl, info[2])
      if options.show_changes and (
          (i < len(unreleased_workflow_versions) and info[3] != unreleased_workflow_versions[i].name)
          or (i >= len(unreleased_workflow_versions) and info[3] != "Unscheduled")):
        print "* [{key}]({url}/{key}) {summary} (**{user}**) (was {prevSprint}, now {curSprint})".format(key=info[0], url=jira_issue_url, summary=md_friendly_summary, user=info[1], prevSprint=info[3], curSprint=unreleased_workflow_versions[i].name)
      else:
        print "* [{key}]({url}/{key}) {summary} (**{user}**)".format(key=info[0], url=jira_issue_url, summary=md_friendly_summary, user=info[1])
      key = info[0]
      if len(unreleased_workflow_versions) <= sprints_to_schedule:
        version = unreleased_workflow_versions[i]
        if not dry_run:
          soapclient.service.updateIssue(auth, key, [{"id": "fixVersions", "values": [version.id] }])
          update_subtasks(soapclient, auth, key, version.id)
      else:
        if not dry_run:
          soapclient.service.updateIssue(auth, key, [{"id": "fixVersions", "values": [] }])
          update_subtasks(soapclient, auth, key, None)

    print "\n"
