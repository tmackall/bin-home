#!/usr/bin/env python2.6

import subprocess
import re
import json
import shlex
import warnings

class CheckCallError(OSError):
  """CheckCall() returned non-0."""
  def __init__(self, command, cwd, retcode, stdout, stderr=None):
    OSError.__init__(self, command, cwd, retcode, stdout, stderr)
    self.command = command
    self.cwd = cwd
    self.retcode = retcode
    self.stdout = stdout
    self.stderr = stderr

def CheckCall(command, cwd=None):
  """Like subprocess.check_call() but returns stdout.

  Works on python 2.4
  """
  try:
    process = subprocess.Popen(command, cwd=cwd,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    std_out, std_err = process.communicate()
  except OSError, e:
    raise CheckCallError(command, cwd, e.errno, None)
  if process.returncode:
    raise CheckCallError(command, cwd, process.returncode, std_out, std_err)
  return std_out, std_err

def CheckCallWithPipe(command1, command2, cwd=None):
  """Like subprocess.check_call() but returns stdout.

  Works on python 2.4
  """
  try:
    process1 = subprocess.Popen(command1, cwd=cwd,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    std_out1, std_err1 = process1.communicate()

    process2 = subprocess.Popen(command2, cwd=cwd,
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    std_out, std_err = process2.communicate(input=std_out1)

  except OSError, e:
    command = "%s | " % command1
    command += command2
    raise CheckCallError(command, cwd, e.errno, None)
  if process1.returncode:
    raise CheckCallError(command1, cwd, process1.returncode, std_out1, std_err1)
  if process2.returncode:
    raise CheckCallError(command2, cwd, process2.returncode, std_out, std_err)
  return std_out, std_err

def GsqlQuery(sql_query, server):
  """Runs a gerrit gsql query and returns the result"""
  warnings.warn("Moved to the gerrit module.", DeprecationWarning, stacklevel=2)
  gsql_cmd = ['ssh', '-p', '29418', server, 'gerrit', 'gsql', '--format',
              'JSON', '-c', sql_query]
  try:
    (gsql_out, gsql_stderr) = CheckCall(gsql_cmd)
  except CheckCallError, e:
    print "return code is %s" % e.retcode
    print "stdout and stderr is\n%s%s" % (e.stdout, e.stderr)
    raise

  new_out = gsql_out.replace('}}\n', '}}\nsplit here\n')
  return new_out.split('split here\n')

def FindLOSTLink(changeId, server):
  """Looks for an existing jira entry link in the change comments"""
  warnings.warn("Moved to the gerrit module.", DeprecationWarning, stacklevel=2)
  sql_query = ("\"SELECT message FROM change_messages WHERE change_id = "
               "(SELECT change_id FROM changes WHERE change_key = \'%s\')\""
                % changeId)
  change_messages = GsqlQuery(sql_query, server)

  jira_url = re.escape('https://jira.qualcomm.com/jira/browse/QUICLOST-')
  for json_str in change_messages:
#    print "json str is\n%s" % json_str
    if not re.search(jira_url, json_str):
      continue

    json_dict = json.loads(json_str, strict=False)
    if "type" in json_dict and json_dict["type"] == "row":
#      print "message is %s" % json_dict["columns"]["message"]
      id = re.search(jira_url + r'(\d*)', json_dict["columns"]["message"])
      if id:
#        print "id is %s" % id.group(1)
        return id.group(1)

def GetEmailFromAcctId(account_id, server):
  """Returns the preferred email address associated with the account_id"""
  warnings.warn("Moved to the gerrit module.", DeprecationWarning, stacklevel=2)
  sql_query = ("\"SELECT preferred_email FROM accounts WHERE account_id = %s\""
               % account_id)
  email_addr = GsqlQuery(sql_query, server)

  json_dict = json.loads(email_addr[0], strict=False)
  #print "email address is %s" % json_dict["columns"]["preferred_email"]
  if "columns" in json_dict:
    return json_dict["columns"]["preferred_email"]
  else:
    print ("columns not in json_dict\nemail_addr is: "
           "%s\njson_dict is:\n%s" % (email_addr, json_dict))
    raise Exception()

def GetUsernameFromEmail(email_addr, server):
  """Returns the username associated with the email address"""
  warnings.warn("Moved to the gerrit module.", DeprecationWarning, stacklevel=2)
  sql_query = ("\"SELECT external_id FROM account_external_ids where "
               "external_id LIKE 'username:%%' AND account_id = (SELECT "
               "DISTINCT account_id FROM account_external_ids WHERE "
               "email_address = '%s')\"" % email_addr)
  username = GsqlQuery(sql_query, server)

  json_dict = json.loads(username[0], strict=False)
  if "columns" in json_dict:
    user_name = re.search('username:(.*)',
                          json_dict["columns"]["external_id"]).group(1)
  else:
    print ("columns not in json_dict\nemail_addr is: "
           "%s\njson_dict is:\n%s" % (email_addr, json_dict))
    user_name = "Not found"
  #print "username is %s" % user_name
  return user_name

def GetPrefEmailFromEmail(email_addr, server):
  """Returns the preferred email address associated with the email address"""
  warnings.warn("Moved to the gerrit module.", DeprecationWarning, stacklevel=2)
  sql_query = ("\"SELECT preferred_email FROM accounts WHERE account_id = ("
               "SELECT DISTINCT account_id FROM account_external_ids WHERE "
               "email_address = '%s')\"" % email_addr)
  email_addr = GsqlQuery(sql_query, server)

  json_dict = json.loads(email_addr[0], strict=False)
  #print "email address is %s" % json_dict["columns"]["preferred_email"]
  if "columns" in json_dict:
    return json_dict["columns"]["preferred_email"]
  else:
    print ("columns not in json_dict\nemail_addr is: "
           "%s\njson_dict is:\n%s" % (email_addr, json_dict))
    raise Exception()

def AddCommentToChange(server, project, msg, commit, args=None):
  """Inserts a comment into the change"""
  warnings.warn("Moved to the gerrit module.", DeprecationWarning, stacklevel=2)
  msg = "\'--message=" + msg + "'"
  comment_cmd = ['ssh', '-p', '29418', server, 'gerrit', 'review', '--project',
                 project, msg, commit]
  if args:
    comment_cmd.append(args)

  try:
    (comment_out, comment_stderr) = CheckCall(comment_cmd)
  except CheckCallError, e:
    print "return code is %s" % e.retcode
    print "stdout and stderr is\n%s%s" % (e.stdout, e.stderr)
    raise

def GerritQuery(query, server):
  """Runs a gerrit query and returns the result"""
  warnings.warn("Moved to the gerrit module.", DeprecationWarning, stacklevel=2)
  query_cmd = ['ssh', '-p', '29418', server, 'gerrit', 'query', '--format',
              'JSON', query]
  try:
    (query_out, query_stderr) = CheckCall(query_cmd)
  except CheckCallError, e:
    print "return code is %s" % e.retcode
    print "stdout and stderr is\n%s%s" % (e.stdout, e.stderr)
    raise

  new_out = query_out.replace('}\n', '}}\nsplit here\n')
  new_list = new_out.split('}\nsplit here\n')
  new_list.remove('')
  return new_list

def GerritReview(changelist, comment, args, server):
  """Runs a gerrit query and returns the result"""
  warnings.warn("Moved to the gerrit module.", DeprecationWarning, stacklevel=2)
  args_list = shlex.split(args)
  changes_list = shlex.split(changelist)
  review_cmd = ['ssh', '-p', '29418', server, 'gerrit', 'review']
  review_cmd.extend(args_list)
  review_cmd.extend(['--message=\'', comment, '\''])
  review_cmd.extend(changes_list)
  try:
    (review_out, review_stderr) = CheckCall(review_cmd)
  except CheckCallError, e:
    print "return code is %s" % e.retcode
    print "stdout and stderr is\n%s%s" % (e.stdout, e.stderr)
    raise

def getMembers(groupName):
  """Returns the list of members of a qgroup"""
  command = ['ldapsearch', '-LLL', '-h', 'edir-sd', '-p', '389', '-x', '-b',
             'ou=qgroups,ou=groups,o=qualcomm', 'cn=%s' % groupName, 'member']
  process = subprocess.Popen(command, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
  std_out, std_err = process.communicate()
  # Need to turn this into a list of members
  members = []
  for member in std_out.split():
    match = re.search('uid=(\w+),ou=people,o=qualcomm', member)
    if match:
      members.append(match.group(1))
  return members
