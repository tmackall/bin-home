#!/usr/bin/python
# Copyright (c) 2011 QUALCOMM Incorporated.  All Rights Reserved.
# QUALCOMM Proprietary and Confidential.
#
#The primary objective of this  script is to generate Distributed Test Bed properties to select test bed  as defined in pl_map module for given manifest branch.
#This script will provide the flexibility to users can override the default sites defined in the pl_map module and have the freedom to select the test bed site.

import sys
import optparse
import pl_map
import pl_values
import re
import subprocess

parser = optparse.OptionParser(usage="USAGE:%prog [options] filename")
parser.add_option("-b", "--branch", dest="branchname",
                  help="Select one of the manifest branch defined in pl_map \n"
                       "Example:gingerbread|gingerbread_rel|gingerbread_house etc.. ")
parser.add_option("-o", "--override_default_site", dest="override_default_site",
                  help="Override some of the targets default site value <target@site> or all targets <all@site> \n\n"
                       "Example:msm8660_surf@hyderabad,msm7627_surf@boulder #To override some of the default targets  \n "
                       "Example:all@hyderabad  To override all default targets to one site")
parser.add_option("-t", "--targets ", dest="targets_list",
                  help="Create DLTB properties only for these targets \n  Example:msm7627_surf,msm8660_surf,etc..")
parser.set_usage("%prog -b <branchname> -o <target@site>,<target@site>")

mandatories = ['branchname']
(opts, args) = parser.parse_args()
for m in mandatories:
  if not opts.__dict__[m]:
    parser.error("%s is a mandatory argument \n\n\n ****Usage: Please Run \"%s -h\"\n\n" % (m,sys.argv[0]))
    sys.exit(1)

#Get list of DLTB supported sites to validate override site parameter
list_dltb_supported_sites = list(pl_values.test_bed_site())
print "DLTB supported sites: %s" % list_dltb_supported_sites
default_test_bed = pl_values.test_bed_site.BOULDER
base_test_bed = pl_values.test_bed_site.BOULDER


#Reading User Parameters into respective lists
pl_site_map = pl_map.PLMap(pl_map.PL)
list_pl_site_map = pl_site_map.getTargetsSiteByBranch(opts.branchname)

#Get targets enabled in CI from Android_main/targets_by_branch property
cmd = 'ectool getProperty /projects/Android_main/targets_by_branch/' + opts.branchname
cmd_out = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
ci_targets, property_error = cmd_out.communicate()
ci_targets_site_list = []

# The given input branch name not defined in pl_map and EC properties, don't create any DLTB properties
if ( property_error == "" ):
  if list_pl_site_map:
    list_target_site_map = list(set(list_pl_site_map))
    print "Targets defined PL_MAP: %s" % list_target_site_map
  else:
    print "NOTE: The %s branch not defined in pl_map, if there any active PL's, please add branch pl mapping in pl_map" % opts.branchname
    list_target_site_map = []

  ci_targets = ci_targets.rstrip()
  ci_targets_list = ci_targets.split(" ")
  print "Targets Enabled in CI: %s" % ci_targets_list
  for mytarget in ci_targets_list:
    ci_targets_site_list.append(mytarget + '@' +  default_test_bed)
else:
  if list_pl_site_map:
    list_target_site_map = list(set(list_pl_site_map))
  else:
    print "ERROR:The branch %s not defined in pl_map and  EC properties" % opts.branchname
    print "Property Error: %s " % property_error
    sys.exit(1)


override_default_site = []
if opts.override_default_site:
   override_default_site = opts.override_default_site.split(',')

override_all_targets_default_test_bed = ""

for override_site in override_default_site:
  m = re.match(r'(all)@(.*)', override_site, re.M|re.I)
  if m:
    if (len(override_default_site) == 1  and m.group(2) in list_dltb_supported_sites):
      override_all_targets_default_test_bed = m.group(2)
      print "Override all targets test bed site to: %s " % override_all_targets_default_test_bed
    else:
      parser.error("Error: Invalid Override test bed site parameter!!, Please select on of the site from this dltb supported sites list:%s" % list_dltb_supported_sites)
      sys.exit(1)

#Create final target site map list as defined in pl_map script and also  based on user inputs
dict_target_site_map = {}
if override_all_targets_default_test_bed:
  final_target_site_map_list = ci_targets_site_list + list_target_site_map
else:
  final_target_site_map_list = ci_targets_site_list + list_target_site_map + override_default_site

for index in final_target_site_map_list:
  matchObj = re.match( r'(.*)@(.*)', index, re.M|re.I)
  if matchObj:
    if override_all_targets_default_test_bed:
      dict_target_site_map[matchObj.group(1)] = override_all_targets_default_test_bed
    else:
      if ( matchObj.group(2)  in list_dltb_supported_sites):
        dict_target_site_map[matchObj.group(1)] = matchObj.group(2)
      else:
        parser.error("Error: Invalid Override test bed site parameter!!, Please select on of the site from this DLTB supported sites list:%s" % list_dltb_supported_sites)
        sys.exit(1)
  else:
    print "Override parameters in wrong format !!"

targets_list = []

if opts.targets_list:
  input_targets_list = opts.targets_list.split(',')
  print "List of targets passed as argument:%s" % input_targets_list
  temp_dict_target_site_map = {}
  for mytarget in input_targets_list:
    mysite = dict_target_site_map.get(mytarget,default_test_bed)
    temp_dict_target_site_map[mytarget] = mysite
    if mysite != default_test_bed:
      cmd = 'ectool setProperty /myJob/DLTB/' + mytarget + '/site'+ " " + mysite + '_'
      print "Creating DLTB property: %s" % cmd
      subprocess.call(cmd, shell=True)

  if default_test_bed not in temp_dict_target_site_map.values():
    base_test_bed = temp_dict_target_site_map.values()[-1]

  myjob_sites_list = list(set(temp_dict_target_site_map.values()))
  myjob_sites = ' '.join(myjob_sites_list)

else:
  print "Target to site map based on the input arguments: %s" % dict_target_site_map
  print "List of Targets Enabled in CI: %s" % ci_targets_list
  for target_name in ci_targets_list:
    mysite = dict_target_site_map[target_name]
    if mysite != default_test_bed:
      cmd = 'ectool setProperty /myJob/DLTB/' + target_name + '/site'+ " " + mysite + '_'
      print "Creating DLTB property: %s" % cmd
      subprocess.call(cmd, shell=True)

  if default_test_bed not in dict_target_site_map.values():
    base_test_bed = dict_target_site_map.values()[-1]

  myjob_sites_list = list(set(dict_target_site_map.values()))
  myjob_sites = ' '.join(myjob_sites_list)


print "default task host site: %s\n" % base_test_bed
if base_test_bed != default_test_bed:
  cmd = 'ectool setProperty /myJob/DLTB/default' + " " + base_test_bed + '_'
  print "Creating DLTB property for default testbed: %s" % cmd
  subprocess.call(cmd, shell=True)

cmd = 'ectool setProperty /myJob/DLTB/selected_sites' + " " + "'" + myjob_sites + "'"
print "Creating current job selected sites property: %s" % cmd
subprocess.call(cmd, shell=True)
