#!/usr/bin/env python2.6

import re
import json
import shlex

from common import CheckCallError
from common import CheckCall
from common import CheckCallWithPipe

def GsqlQuery(sql_query, server):
  """Runs a gerrit gsql query and returns the result"""
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

def GerritQuery(query, server, current_patch_set=False):
  """Runs a gerrit query and returns the result"""
  query_cmd = ['ssh', '-p', '29418', server, 'gerrit', 'query', '--format',
              'JSON', query]
  if current_patch_set:
    query_cmd.insert(query_cmd.index('query')+1, '--current-patch-set')
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
  """Runs a gerrit review cmd with the given arguments"""
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

def getChangeInfoFromURL(url):
  """Returns the a tuple containing the server the change is located on
     and the change id. (server, change_id)"""
  match = re.search('https?://(.*?)/(?:#change,|#/c/)?([0-9]+).*', url)
  if match:
    ret = match.groups()
  else:
    ret = (None, None)
  return ret

def getAliasesForChange(server, change_num):
  aliases = []
  aliases.append('https://%s/%s' % (server, change_num))
  aliases.append('https://%s/#change,%s' % (server, change_num))
  aliases.append('https://%s/#/c/%s/' % (server, change_num))
  return aliases

def getAliasesForURL(url):
  server, change_num = getChangeInfoFromURL(url)
  aliases = getAliasesForChange(server, change_num)
  return aliases

def getGerritChangeFromURL(url):
  server, change_id = getChangeInfoFromURL(url)
  if not server:
    print "Error: %s is not a valid gerrit URL" % url
    return None
  query = "change:%s" % change_id
  try:
    change_data = GerritQuery(query, server, current_patch_set=True)
  except:
    print "Error: Error contacting gerrit server for change data."
    return None
  if len(change_data) < 2:
    print "Error: No change %s on server %s" % (change_id, server)
    return None
  change_dict = json.loads(change_data[0], strict=False)
  return change_dict
