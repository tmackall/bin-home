#!/usr/bin/env python2.6

from suds.client import Client
from base64 import b64encode

# In alpha order by key, keep it that way.
_ids = { 'au' : 'customfield_10163',
         'au_master' : 'customfield_10167',
         'cc_groups' : 'customfield_10062',
         'cc_list' : 'customfield_10060',
         'change_id' : 'customfield_10183',
         'code_poc' : 'customfield_10181',
         'code_ptr' : 'customfield_10184',
         'code_space' : 'customfield_10177',
         'description' : 'description',
         'fix_versions' : 'fixVersions',
         'freeze_date' : 'customfield_10168',
         'gerrit_patch' : 'customfield_10166',
         'gerrit_link' : 'customfield_10164',
         'git_branch' : 'customfield_10165',
         'lic_notes' : 'customfield_10180',
         'lic_ptr' : 'customfield_10182',
         'lost_resolution' : 'customfield_10217',
         'notes' : 'customfield_10172',
         'patch_id' : 'customfield_10166',
         'refnum_cust' : 'customfield_10179',        # CR numbers, Case numbers, and Customers
         'release_date' : 'customfield_10169',
         'release_url' : 'customfield_10178',
         'sba' : 'customfield_10401',
         'story_points' : 'customfield_10001',
         'submitter' : 'customfield_10032',
         'targets' : 'customfield_10240',
}

# In alpha order by key, keep it that way.
_issue_types = { 'au_scan' : '11',
               'new_code_scan' : '13',
               'task' : 3,
}

_status_resolution = {
  'FULLY_APPROVED' : ['Closed', 'Fully Approved'],
  'ARCH_APPROVED_ONLY' : ['Closed', 'Architecture Approved Only'],
  'HOLD' : ['Monitor (On Hold)', 'None'],
  'IN_LEGAL' : ['In Legal', 'None'],
  'REJECTED' : ['Closed', 'Rejected'],
  'WITHDRAWN' : ['Closed', 'Withdrawn'],
}

default_server='jira.qualcomm.com'
default_authfile=''

def _get_auth(authFile, server):
  if authFile:
    _authFile  = authFile
  else:
    _authFile = default_authfile

  if server:
    _server = server
  else:
    _server = default_server

  assert _authFile
  assert _server

  url = 'https://' + _server + '/jira/rpc/soap/jirasoapservice-v2?wsdl'
  soapclient = Client(url)

  with open(_authFile) as file:
    user = file.readline().strip()
    passwd = file.readline().strip()

  auth = soapclient.service.login(user, passwd)
  return (soapclient, auth)



def get_default_authfile():
  return default_authfile

def get_default_server():
  return default_server

def set_default_authfile(authFile):
  global default_authfile
  default_authfile=authFile

def set_default_server(server):
  global default_server
  default_server=server


def add_attachment_to_JIRA(key, attachment, attachmentName=None, authfile=None, server=None):
  (soapclient, auth) = _get_auth(authFile, server)

  if attachment:
    _attachmentName = attachmentName
    if not _attachmentName:
      _attachmentName = attachment
    with open(attachment) as fileobj:
      data = fileobj.read()
    b64data = b64encode(data)
    soapclient.service.addBase64EncodedAttachmentsToIssue(auth, key, [_attachmentName], [b64data])
  else:
    raise ValueError("No attachment specified.")

def add_comment_to_JIRA(key, comment, authFile=None, server=None):
  (soapclient, auth) = _get_auth(authFile, server)

  if comment:
    soapclient.service.addComment(auth, key, {'body': notes})

def append_to_fields(key, authFile=None, server=None, **kwargs):
  (soapclient, auth) = _get_auth(authFile, server)

  issue = get_issue(key, authFile, server)
  customFields = issue.customFieldValues
  field_array = []
  for key, value in kwargs.iteritems():
    id = _ids[key]
    if id:
      if id in issue:
        old_value = issue[id]
      else:
        for c in customFields:
          if c.customfieldId == id:
            old_value = c.values
            break
          else:
            old_value = []
      old_value.extend(value)
      field_array.append({'id': id, 'values':old_value})

  soapclient.service.updateIssue(auth, key, field_array)

def create_issue(project, summary, components, issueType, 
                   authFile=None, server=None, **kwargs):
  assert _issue_types[issueType]

  (soapclient, auth) = _get_auth(authFile, server)

  server_components = get_components(project, authFile, server)
  component_ids={}
  for c in server_components:
    component_ids[c['name']] = c['id']

#XXX: Hack to be backward compatible with component indecies from the
# old lost scripts
  sorted_components = sorted(server_components, key=lambda k: k['id'])

  component_array = []
  for component in components.split(','):
    if component.strip() in component_ids:
      component_array.append({'id': component_ids[component]})
#XXX: Continued Hack from above
    else:
      try:
        int(component)
      except:
        #Throwing away components we don't understand
        pass
      else:
        if int(component)-1 < len(sorted_components):
          component_array.append({'id': sorted_components[int(component)-1]['id']})
  if component_array:
    issue_key = soapclient.service.createIssue(auth,
      {'project':project,
       'components' : component_array,
       'type' : _issue_types[issueType],
       'summary' : summary
      })
    set_fields(issue_key['key'], authFile, server, **kwargs) 
    return issue_key
  else:
    print "None of the specified components could be found in the %s project." % project
    print "Please select a component from the following:"
    for c in server_components:
      print "  %s" % c['name']
    return 0

def create_version(project, name, releaseDate, authFile=None, server=None, **kwargs):
  (soapclient, auth) = _get_auth(authFile, server)
  ver = {'name':name, 'releaseDate':releaseDate}
  for key, value in kwargs.iteritems():
    ver[key] = value
# @TODO: If release date is something other than a python DateTime, convert
  new_version = soapclient.service.addVersion(auth, project, ver)
  return new_version

def simple_resolve_issue(key, authFile=None, server=None):
  (soapclient, auth) = _get_auth(authFile, server)

  action_id = ''
  for action in get_available_actions(key, authFile, server):
    if action.name == 'Resolve Issue':
      action_id = action.id
      break
  if action_id:
    issue = soapclient.service.progressWorkflowAction(auth, key, action_id, [])
  else:
    issue = None
  return issue

def get_available_actions(key, authFile=None, server=None):
  (soapclient, auth) = _get_auth(authFile, server)
  actions = soapclient.service.getAvailableActions(auth, key)
  return actions

def get_issue(key, authFile=None, server=None):
  (soapclient, auth) = _get_auth(authFile, server)
  issue = soapclient.service.getIssue(auth, key)
  return issue

def get_worklogs_from_issue(key, authFile=None, server=None):
  (soapclient, auth) = _get_auth(authFile, server)
  worklogs = soapclient.service.getWorklogs(auth, key)
  return worklogs

def get_comments(key, authFile=None, server=None):
  (soapclient, auth) = _get_auth(authFile, server)
  comments = soapclient.service.getComments(auth, key)
  return comments

def get_issues_with_query(query, maxIssues=10000, authFile=None, server=None):
  (soapclient, auth) = _get_auth(authFile, server)
  issues = soapclient.service.getIssuesFromJqlSearch(auth, query, maxIssues)
  return issues

def get_components(project, authFile=None, server=None):
  (soapclient, auth) = _get_auth(authFile, server)
  components = soapclient.service.getComponents(auth, project)
  return components

def get_versions(project, authFile=None, server=None):
  (soapclient, auth) = _get_auth(authFile, server)
  versions = soapclient.service.getVersions(auth, project)
  return versions

def set_fields(issue_key, authFile=None, server=None, **kwargs):
  (soapclient, auth) = _get_auth(authFile, server)

  field_array = []
  for key, value in kwargs.iteritems():
    if key in _ids and value is not None:
      field_array.append({'id':_ids[key], 'values': [value]})
  soapclient.service.updateIssue(auth, issue_key, field_array)

def set_issue_status(key, action, resolution, lost_resolution=None, authFile=None, server=None):
  (soapclient, auth) = _get_auth(authFile, server)
  avail_actions = soapclient.service.getAvailableActions(auth, key)
  for i in avail_actions:
    if i['name'] == action:
      action_id = i['id']
  if not action_id:
    # not an available action
    return 1
  resolution_array = [{'id':'resolution', 'values':[resolution]},]
  if lost_resolution:
    resolution_array.append({'id':_ids['lost_resolution'], 'values': [lost_resolution]})
  soapclient.service.progressWorkflowAction(auth, key, action_id, resolution_array)
  return 0

def get_fields_from_issue(key, authFile=None, server=None, *fields):
  (soapclient, auth) = _get_auth(authFile, server)
  issue = soapclient.service.getIssue(auth, key)
  customFields = issue.customFieldValues

  value = ""
  fieldIds = {}
  for field in fields:
    id = _ids[field]
    if id:
      if id in issue:
        value = issue[id]
      else:
        for c in customFields:
          if c.customfieldId == id:
            value = c.values
            break
          else:
            value = ""
    else:
      print "id for field not found"
      exit(1)

    fieldIds[field] = value
  return fieldIds
