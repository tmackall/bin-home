#!/usr/bin/env python2.6
#

import re
import json
from optparse import OptionParser
import os
from suds.client import Client
import sys
import string

#local imports
import common

def get_changeID_from_GerritChangeKey (changeKey, server):
  """get_changeID_from_GerritChangeKey : given a change key (40 character
  hexidecimal, prepended with the upper case letter 'I') the change id
  associated with that change key is returned.

  """

  changeNum = "0"
  if changeKey:
    # Get the change id associated with the change key
    sql_query = ("\"SELECT change_id FROM changes WHERE change_key = \'%s\'\""
                      % changeKey)
    changeNums = common.GsqlQuery(sql_query, server)

    if len(changeNums) < 2:
      changeNum = "0"
    else:
      json_dict = json.loads(changeNums[0], strict=False)
      changeNum = json_dict['columns']['change_id']

  return changeNum


def get_changeKey_from_GerritChangeID (changeNum, server):
  """get_changeKey_from_GerritChangeID : given a change id return the associated
  change key (40 character hexidecimal, prepended with the upper case letter
  'I')

  """

  changeKey = "0"
  if changeNum:
    # Get the change id associated with the change key
    sql_query = ("\"SELECT change_key FROM changes WHERE change_id = %s\""
                      % changeNum)
    changeKeys = common.GsqlQuery(sql_query, server)

    if len(changeKeys) < 2:
      changeKey = "0"
    else:
      json_dict = json.loads(changeKeys[0], strict=False)
      changeKey = json_dict['columns']['change_key']

  return changeKey


def get_last_revision_from_GerritChangeID (changeNum, server):
  """get_last_revision_from_GerritChangeID : given a change id, the last patch
  set revision number for that change is returned

  """

  last_revision = "0"
  if changeNum:
    # Get the revisions associated with the change id
    sql_query = ("\"SELECT revision FROM patch_sets WHERE change_id = %s\""
                      % changeNum)
    change_revisions = common.GsqlQuery(sql_query, server)

    # We subtract 1 because the last entry in the sql_query response is the
    # query statistics
    num_change_revisions = len(change_revisions) - 1

    i = 0
    revision_list = []
    while i < num_change_revisions:
      json_dict = json.loads(change_revisions[i], strict=False)
      revision = json_dict['columns']['revision']
      revision_list.append(revision)
      i += 1

    last_revision = revision_list[num_change_revisions-1]
  return last_revision

def gen_patchID_from_GerritChangeID (changeNum, server):
  """gen_patchID_from_GerritChangeID : given a gerrit change id, the last patch
  set revision in the gerrit change is used to generate a git patch-id.

  NOTE: this routine expects GIT_DIR will be set or the script will be run from
  the proper git repository

  """

  patch = "0"
  if changeNum:
    last_revision = get_last_revision_from_GerritChangeID(changeNum, server)
    #Get patch id for last revision
    range = "%s^.." % last_revision
    range += last_revision
    patch_cmd = ['git', 'log', '-p', range ]
    patch_id_cmd = ['git', 'patch-id']
    try:
      (patch_set_out, patch_stderr) = common.CheckCallWithPipe(patch_cmd,
                                                               patch_id_cmd)
    except common.CheckCallError, e:
      print "return code is %s" % e.retcode
      print "stdout is\n%s\nstderr is\n%s" % (e.stdout, e.stderr)
      raise

    patch_set = patch_set_out.split()
    patch = patch_set[0]
  return patch

def gen_patchID_from_file (patch):
  """ Generate a patch ID for a given patch using git patch-id """

  patch_cmd = ['cat', patch]
  patch_id_cmd= ['git', 'patch-id']

  try:
    (patch_set_out, patch_stderr) = common.CheckCallWithPipe(patch_cmd,
                                                             patch_id_cmd)
  except common.CheckCallError, e:
    print "return code is %s" % e.retcode
    print "stdout is\n%s\nstderr is\n%s" % (e.stdout, e.stderr)
    raise

  patch_set = patch_set_out.split()
  patch = patch_set[0]
  return patch

def gen_patchID_from_GerritChangeKey (changeKey, server):
  """gen_patchID_from_GerritChangeKey: given a change key (40 character
  hexidecimal, prepended with the upper case letter 'I') the last patch set
  revision in the gerrit change associated with that change key is used to
  generate a git patch-id.

  NOTE: this routine expects GIT_DIR will be set or the script will be run from
  the proper git repository
  """

  patch_id = "0"
  if changeKey:
    changeNum = get_changeID_from_GerritChangeKey(changeKey, server)

    if changeNum:
      patch_id = gen_patchID_from_GerritChangeID(changeNum, server)

  return patch_id


def get_git_path_from_GerritChangeKey (changeKey, server, projectsRoot):
  """gen_git_path_from_GerritChangeKey: given a change key (40 character
  hexidecimal, prepended with the upper case letter 'I') return the full
  pathname to the project git directory

  """

  # Get the project name associated with the change key
  project_path = ""
  if changeKey:
    sql_query = ("\"SELECT dest_project_name FROM changes WHERE change_key = "
                      "\'%s\'\"" % changeKey)
    query_result = common.GsqlQuery(sql_query, server)

    json_dict = json.loads(query_result[0], strict=False)
    project = json_dict['columns']['dest_project_name']

    project_path = "%s/" % projectsRoot
    project_path += project
    project_path += "/.git"

  return project_path

def get_patch_filenames_from_GerritChangeKey(changeKey, server):
  """get_patch_filenamess_from_GerritChangeKey : given a change key (40
  character hexidecimal, prepended with the upper case letter 'I') a list of
  files added to the gerrit change that end in ".patch" is returned.

  """

  patch_list = []
  if changeKey:
    changeNum = get_changeID_from_GerritChangeKey (changeKey, server)

    if changeNum:
      # Get the files associated with the change id
      sql_query = ("\"SELECT file_name FROM account_patch_reviews WHERE "
                        " change_id = %s\"" % changeNum)
      change_files = common.GsqlQuery(sql_query, server)

      # We subtract 1 because the last entry in the sql_query response is the
      # query statistics
      num_change_files = len(change_files) - 1

      i = 0
      while i < num_change_files:
        json_dict = json.loads(change_files[i], strict=False)
        file_name = json_dict['columns']['file_name']
        pattern = '.patch$'
        aMatch = re.search(pattern, file_name)
        if aMatch:
          patch_list.append(file_name)
        i += 1

  return patch_list

def add_patchID_in_JIRA(change, jira_id, authFile, server, jira_url):
  """add_patchID_in_JIRA: given jira id and change info, calculate the patch ids
  for the given change, then update the jira patch id field.

  NOTE: this routine expects GIT_DIR will be set or the script will not be run
  from the proper git repository

  """

  change_id_field = 'customfield_10183'
  patch_id_field = 'customfield_10166'

  soapclient = Client(jira_url)

  try:
    file = open(authFile)
    user = file.readline()
    user = user.rstrip()
    passwd = file.readline()
    passwd = passwd.rstrip()
  except ValueError:
    print "ERROR: Invalid authentication file."
    exit(2)

  try:
    _jira_id = int(jira_id)
  except ValueError:
    print "ERROR: Invalid jira_id. Number only from QUICLOST-11409"
    exit(1)

  jira_id = 'QUICLOST-' + jira_id

  # Authenticate
  auth = soapclient.service.login(user, passwd)

  # Get jira issue
  issue = soapclient.service.getIssue(auth, jira_id)

  # Get Gerrit Change Ids and create Patch Ids
  patchIDs = ""
  customFields = issue.customFieldValues
  for c in customFields:
    if c.customfieldId == patch_id_field:
      patchIDs = c.values[0]
  if change.startswith('I') and len(change) == 41:
    patchID = gen_patchID_from_GerritChangeKey (change, server)
  elif change.isdigit() and len(change) == 5:
    patchID = gen_patchID_from_GerritChangeID (change, server)
  else:
    print ('WARNING: change ID', change,
             'could not be recognized as a gerrit change ID.')
  if patchID not in patchIDs:
    if patchIDs:
      patchIDs += "\n"
    patchIDs += patchID

  # Append the patch_id to the existing list of patch ids
  if patchIDs:
    # Update patch id field
    soapclient.service.updateIssue(auth, jira_id,
        [{"id": patch_id_field, "values": [patchIDs]} ])

def update_patchIDs_in_JIRA(jira_id, authFile, server, jira_url):
  """update_patchIDs_in_JIRA: given jira id calculate the patch ids from the
  change ids listed in the jira, then update the jira patch id field.

  NOTE: this routine expects GIT_DIR will be set or the script will not be run
  from the proper git repository

  """

  change_id_field = 'customfield_10183'
  patch_id_field = 'customfield_10166'

  soapclient = Client(jira_url)

  try:
    file = open(authFile)
    user = file.readline()
    user = user.rstrip()
    passwd = file.readline()
    passwd = passwd.rstrip()
  except ValueError:
    print "ERROR: Invalid authentication file."
    exit(2)

  try:
    _jira_id = int(jira_id)
  except ValueError:
    print "ERROR: Invalid jira_id. Number only from QUICLOST-11409"
    exit(1)

  jira_id = 'QUICLOST-' + jira_id

  # Authenticate
  auth = soapclient.service.login(user, passwd)

  # Get jira issue
  issue = soapclient.service.getIssue(auth, jira_id)

  # Get Gerrit Change Ids and create Patch Ids
  patchIDs = ""
  customFields = issue.customFieldValues
  for c in customFields:
    if c.customfieldId == change_id_field:
      changeID_list = c.values
      changeID_str = changeID_list[0]
      change_ids =  changeID_str.splitlines()
      for i in range(len(change_ids)):
        print i, change_ids[i]
        if change_ids[i].startswith('I') and len(change_ids[i]) == 41:
          patchID = gen_patchID_from_GerritChangeKey (change_ids[i], server)
        elif change_ids[i].isdigit() and len(change_ids[i]) == 5:
          patchID = gen_patchID_from_GerritChangeID (change_ids[i], server)
        else:
          print ('WARNING: change ID', change_ids[i],
                    'could not be recognized as a gerrit change ID.')
          continue
        if patchID not in patchIDs:
          if i > 0:
            patchIDs += "\n"
          patchIDs += patchID

  # Append the patch_id to the existing list of patch ids
  if patchIDs:
    # Update patch id field
    soapclient.service.updateIssue(auth, jira_id,
        [{"id": patch_id_field, "values": [patchIDs]} ])

def get_ChangeIDs_from_JIRA(jira_id, authFile, jira_url):
  """get_ChangeIDs_from_JIRA : give a jira_id retrieve the change ids from the
  Gerrit change id field

  """

  change_id_field = 'customfield_10183'

  soapclient = Client(jira_url)

  try:
    file = open(authFile)
    user = file.readline()
    user = user.rstrip()
    passwd = file.readline()
    passwd = passwd.rstrip()
  except ValueError:
    print "ERROR: Invalid authentication file."
    exit(2)

  try:
    _jira_id = int(jira_id)
  except ValueError:
    print "ERROR: Invalid jira_id. Number only from QUICLOST-11409"
    exit(1)

  jira_id = 'QUICLOST-' + jira_id

  # Authenticate
  auth = soapclient.service.login(user, passwd)

  # Get jira issue
  issue = soapclient.service.getIssue(auth, jira_id)

  customFields = issue.customFieldValues
  for c in customFields:
    if c.customfieldId == change_id_field:
      changeID_list = c.values
      changeID_str = changeID_list[0]
      change_ids =  changeID_str.splitlines()

  return change_ids

def get_JIRA_issues_from_change_info(change, authFile, server, jira_url):
  """get_JIRA_issues_from_change_info: given a changeID or change key return the
  issues in JIRA that match.

  """

  try:
    file = open(authFile)
    user = file.readline()
    user = user.rstrip()
    passwd = file.readline()
    passwd = passwd.rstrip()
  except ValueError:
    print "ERROR: Invalid authentication file."
    exit(1)

  soapclient = Client(jira_url)
  auth = soapclient.service.login(user, passwd)

  if change.startswith('I') and len(change) == 41:
    changeID = get_changeID_from_GerritChangeKey(change, server)
    changeKey = change
  elif change.isdigit() and len(change) < 35:
    changeKey = get_changeKey_from_GerritChangeID(change, server)
    changeID = change
  else:
    print 'Change argument was not recognizable as a Gerrit change.'
    exit(1)

  soap_query = ('project = QUICLOST and issuetype = "New Code Scan" and '
    '("Gerrit IDs" ~ ' + changeID + ' or "Gerrit IDs" ~ '
    + changeKey + ')' )
#FIXME: figure out what to use instead of an arbitrarily large
#       number to limit the issues returned.
  issues = soapclient.service.getIssuesFromJqlSearch(auth, soap_query, 10000)
  return issues

def get_approved_JIRA_issues_with_patch_ID(patch_ID, proj, authFile, jira_url):
  """ get a list of approved LOST JIRA issues that contain the given patchID """

  try:
    file = open(authFile)
    user = file.readline()
    user = user.rstrip()
    passwd = file.readline()
    passwd = passwd.rstrip()
  except ValueError:
    print "ERROR: Invalid authentication file."
    exit(1)

  soapclient = Client(jira_url)
  auth = soapclient.service.login(user, passwd)

  if proj:
    project_filter = ' and component = "' + proj + '"'
  else:
    project_filter = ''

  soap_query = ('project = QUICLOST and "LOST Resolutions" = "Fully Approved" '
    ' and "Git patch-id" ~ ' + patch_ID + project_filter)
  issues = soapclient.service.getIssuesFromJqlSearch(auth, soap_query, 10000)
  return issues

def update_JIRAs(change, authFile, server, jira_url):
  """update_JIRAs: update the patch-id field of any QUICLOST newcode jira that
  contains the change key or change id associated with 'change'

  """

  issues=get_JIRA_issues_from_change_info(change, authFile, server, jira_url)

  for issue in issues:
    JIRA_key = issue.key
    jira = JIRA_key.replace('QUICLOST-', '')
    add_patchID_in_JIRA(change, jira, authFile, server, jira_url)

if __name__ == '__main__':
  usage = "usage: %prog <required options>"
  parser = OptionParser(usage=usage)
  parser.add_option("--change", dest="change", help="Change identifier*")
  parser.add_option("--server", help="Gerrit server to use")
  parser.add_option("--authFile", help="File containing JIRA authentication")
  parser.add_option("--jiraServer", default="jira.qualcomm.com", help="JIRA "
    "server to update")

  (options, args) = parser.parse_args()

  change=options.change
  authFile = options.authFile
  server = options.server
  jiraServer = options.jiraServer

  jira_url = 'https://' + jiraServer + '/jira/rpc/soap/jirasoapservice-v2?wsdl'

  update_JIRAs(change, authFile, server, jira_url)
