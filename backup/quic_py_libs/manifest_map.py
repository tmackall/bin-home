#!/usr/bin/env python

import sys
import os
from optparse import OptionParser
from optparse import SUPPRESS_HELP
import shlex
import subprocess
import shutil
import warnings
import imp

# Suppress the runtime warning from os.tempnam().
warnings.simplefilter("ignore", category=RuntimeWarning)

def _getRepo():
  cur_dir = os.getcwd()
  temp_dir=os.tempnam('/tmp')
  os.mkdir(temp_dir)
  os.chdir(temp_dir)
  command = 'git clone git://git.quicinc.com/tools/repo'
  cmd_args = shlex.split(command)
  process = subprocess.Popen(cmd_args, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
  stdout, stderr = process.communicate()
  if os.path.exists('repo'):
    sys.path.insert(0, temp_dir + '/repo')
  else:
    print "Could not find repo to import."
    sys.exit(1)
  os.chdir(cur_dir)
  return temp_dir

#script_dir = sys.path[0]

try:
  from manifest_xml import XmlManifest
except:
  repo_dir=_getRepo()
  from manifest_xml import XmlManifest
  shutil.rmtree(repo_dir)

# Local imports
#sys.path[1] = sys.path[0]
#sys.path[0] = script_dir
#print sys.path
#print sys.modules['manifest']
# try:
#   (f, path, description) = imp.find_module('manifest', script_dir)
#   imp.load_module('custom_manifest', f, path, description)
# except ImportError as e:
#   raise Exception(e)

from manifest_repr import GitServerProjectBranch, Manifest
import pl_map

#print sys.modules['manifest_repr']

mapping={}
populated=0
transport_protocols_by_server = { 'review.quicinc.com':{'protocol':'ssh', 'port':29418, 'user':os.environ['USER']},
                                }

def populate():
  global populated
  if populated:
    return
  git_dir_save = None
  if 'GIT_DIR' in os.environ:
    git_dir_save = os.environ['GIT_DIR']
    del os.environ['GIT_DIR']
  cur_dir = os.getcwd()
  temp_dir=os.tempnam('/tmp')
  os.mkdir(temp_dir)
  os.chdir(temp_dir)

  manifest_project_clone_path = {}
  pl_data = pl_map.PLMap(pl_map.ALL_PL)

  for manifest in pl_data.pl_mapping_by_manifest.keys():
    #XXX
    if manifest.branch == '??':
      continue

    manifest_project = GitServerProjectBranch(server=manifest.server, project=manifest.project)

    clone_path = None
    #if the manifest project has already been cloned
    if manifest_project in manifest_project_clone_path:
      clone_path = manifest_project_clone_path[manifest_project]
    else:
      protocol = 'git'
      user = None
      port = None
      if manifest.server in transport_protocols_by_server:
        if 'protocol' in transport_protocols_by_server[manifest.server]:
          protocol = transport_protocols_by_server[manifest.server]['protocol']
        if 'user' in transport_protocols_by_server[manifest.server]:
          user = transport_protocols_by_server[manifest.server]['user']
        if 'port' in transport_protocols_by_server[manifest.server]:
          port = transport_protocols_by_server[manifest.server]['port']

      manifest_project_url = manifest.generateURL(protocol, user=user, port=port)
      clone_path = manifest.server + '_' + manifest.project.replace('/','_')
      #'manifests' directory is required by the manifest parser of the Repo tool
      command = 'git clone %s %s' % (manifest_project_url, clone_path + '/manifests')
      cmd_args = shlex.split(command)

      process = subprocess.Popen(cmd_args, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, cwd=temp_dir)
      stdout, stderr = process.communicate()

      #check to see if clone was successful
      if not os.path.exists(clone_path + '/manifests'):
        raise Exception('Failed to clone %s: %s' % (manifest_project_url, stdout))

      manifest_project_clone_path[manifest_project] = clone_path

    command = "git checkout origin/%s" % manifest.branch
    cmd_args = shlex.split(command)
    try:
      subprocess.check_call(cmd_args, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, cwd=clone_path+'/manifests')
    except CalledProcessError as e:
      raise Exception('Failed to switch to branch origin/%s for project %s from server %s' % (manifest.branch, manifest.project, manifest.server))

    #Include the branch of the manifest project in the map
    #Each branch of a manifest project that has a PL associated with it
    #is mapped to all the manifests (i.e. xml files) of that branch that's used for a PL
    manifest_GSPB = GitServerProjectBranch(server=manifest.server, project=manifest.project, branch=manifest.branch)
    if manifest_GSPB not in mapping:
      mapping[manifest_GSPB] = [manifest]
    else:
      mapping[manifest_GSPB].append(manifest)

    parsed_manifest = XmlManifest(clone_path)
    parsed_manifest.Link(manifest.path)
    for project_name, project in parsed_manifest.projects.iteritems():
      project_server = GitServerProjectBranch.validate_and_decompose_url(project.remote.url)['host']
      project_GSPB = GitServerProjectBranch(server=project_server, project=project_name, branch=project.revisionExpr.replace('refs/heads/',''))
      if project_GSPB not in mapping:
        mapping[project_GSPB] = [manifest]
      else:
        mapping[project_GSPB].append(manifest)

  os.chdir(cur_dir)
  shutil.rmtree(temp_dir)
  if git_dir_save:
    os.environ['GIT_DIR'] = git_dir_save
  populated = 1

#getManifestBranches(project_name, project_branch) is deprecated.
#use getManifests(server_project_branch) instead.
def getManifestBranches(project_name, project_branch):
  if not populated:
    populate()

  server_project_branch = GitServerProjectBranch(server='git-android.quicinc.com', project=project_name, branch=project_branch)
  if server_project_branch in mapping:
    return [manifest.branch for manifest in mapping[server_project_branch]]
  else:
    return []

def getManifests(server_project_branch):
  if not populated:
    populate()
  if server_project_branch in mapping:
    return mapping[server_project_branch]
  else:
    return []

#getProjectBranch(project_name, manifest_branch) is deprecated.
#use getServerProjectBranch(server, project, manifest) instead.
def getProjectBranch(project_name, manifest_branch):
  if not populated:
    populate()

  for server_project_branch, manifests in mapping.iteritems():
    if server_project_branch.project == project_name:
      for manifest in manifests:
        if manifest.branch == manifest_branch:
          return server_project_branch.branch

  return None

def getServerProjectBranch(server, project, manifest):
  if not populated:
    populate()

  for server_project_branch, manifests in mapping.iteritems():
    if server_project_branch.server == server and \
       server_project_branch.project == project and \
       manifest in manifests:

      return server_project_branch

  return None

if __name__ == '__main__':
  parser = OptionParser()
  parser.add_option("--manifest", default='gingerbread', help=SUPPRESS_HELP)
  parser.set_usage("%prog --manifest <manifest_branch_name> < <list_of_changes>")

  (options, args) = parser.parse_args()
  populate()

  #for server_project_branch, manifests in mapping.iteritems():
    #print '%s => %s' % (server_project_branch, manifests)

  #reads the list of changes from STDIN
  for inputLine in sys.stdin.readlines():
    inputLine = inputLine.strip()

    #;; delimits dependent groups
    if (not inputLine) or (';;' in inputLine) or ('|' not in inputLine):
      continue

    project, branch, ref = inputLine.split('|')

    #print "Project:%s Branch:%s Ref:%s" % (project, branch, ref)

    if options.manifest in getManifestBranches(project, branch):
      #e.g. 'refs/changes/00/87700/7'
      ref_split = ref.split('/')
      print "Project:%s Branch:%s Change:%s Patchset:%s" % (project, branch, ref_split[3], ref_split[4])