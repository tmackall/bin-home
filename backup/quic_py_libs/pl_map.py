#!/usr/bin/env python

# Copyright (c) 2011 QUALCOMM Incorporated.  All Rights Reserved.
# QUALCOMM Proprietary and Confidential.

# This module exists to provide mappings among manifest branches,
# target hardware, product lines, actual hardware, prism targets
# and other entities manipulated in the BAIT system.
#
# The raw PL data is in the _mapping_by_pl member of the PLMap class,
# and any updates to PL data should be made in that structure.  Additionally,
# pseudo-PL data is maintained in the _mapping_by_pseudo_pl structure.
# All other mappings are generated from this raw data.
#
# The primary objective for this module is to enable automated updating of
# PRISM CR's when various events occur in the git repositories. For that
# reason the PL names follow the naming convention used in PRISM.
#
# The module is also intended to support automatic selection of PL and
# non-PL target products for BAIT operations (e.g. preflight, AU
# generation and testing, Lookahead, etc).
#
# PLMap methods provide access to the information when pl_map is imported
# as a module.  pl_map can also be run from the command line and will
# print the requested data to stdout.

import sys
from optparse import OptionParser

# Local imports
from manifest_repr import GitServerProjectBranch, Manifest
from pl_values import linux_branch, target_product, actual_hardware, test_bed_site

# Predefined product line sets.
#   PL consists of only approved product lines.
#   PSEUDO_PL consists of BAIT-supported software/target combinations for which
#      no product line exists.
#   ALL_PL consists of the union of PL and PSEUDO_PL lines
PL = 'PL'
PSEUDO_PL = 'PSEUDO_PL'
ALL_PL = 'ALL_PL'
PLTypes = frozenset([PL, PSEUDO_PL, ALL_PL])

class PLMap(object):

  # PL and Pseudo-PL information is captured in the (private by convention) structures
  # below.  PLMap clients should *not* accesse these directly, as the implementation
  # or presence of these maps could changes at any time.

  # ADD PLs HERE
  # '<PL_NAME>':{'manifest':Manifest(branch='<manifest_branch>'), 'target_product':'<hardware_target>', 'site':'<site>', 'prism_target':'<prism_target>'},
  _mapping_by_pl = {
    'MSM8960.LA.1.0':{'manifest':Manifest(branch=linux_branch.GB), 'target_product':target_product.MSM8960, 'site':test_bed_site.BOULDER, 'prism_target':'MSM8960'},
    'APSS.LA.1.0':{'manifest':Manifest(branch=linux_branch.GB), 'target_product':target_product.MSM8960, 'site':test_bed_site.BOULDER, 'prism_target':'MSM8960'},
    'MSM8660.LA.3.2':{'manifest':Manifest(branch=linux_branch.GB_HOUSE), 'target_product':target_product.MSM8660_SURF, 'site':test_bed_site.BOULDER, 'prism_target':'MSM8660'},
    'MSM8660.LA.3.1':{'manifest':Manifest(branch=linux_branch.GB_HOUSE), 'target_product':target_product.MSM8660_SURF, 'site':test_bed_site.BOULDER, 'prism_target':'MSM8660'},
    'MSM8660.LA.3.0':{'manifest':Manifest(branch=linux_branch.GB_HOUSE), 'target_product':target_product.MSM8660_SURF, 'site':test_bed_site.BOULDER, 'prism_target':'MSM8660'},
    'MSM8260.LA.2.2':{'manifest':Manifest(branch=linux_branch.GB_HOUSE), 'target_product':target_product.MSM8660_SURF, 'site':test_bed_site.BOULDER, 'prism_target':'MSM8660'},
    'MSM8660.LA.2.1':{'manifest':Manifest(branch=linux_branch.GB_HOUSE), 'target_product':target_product.MSM8660_SURF, 'site':test_bed_site.BOULDER, 'prism_target':'MSM8660'},
    'MSM8260.LA.2.0':{'manifest':Manifest(branch=linux_branch.GB_HOUSE), 'target_product':target_product.MSM8660_SURF, 'site':test_bed_site.BOULDER, 'prism_target':'MSM8660'},
    'MSM8260.LA.2.0.3.55.1':{'manifest':Manifest(branch=linux_branch.GB_HOUSE), 'target_product':target_product.MSM8660_SURF, 'site':test_bed_site.BOULDER, 'prism_target':'MSM8660'},
    'MSM8260.LA.2.0.3.55.2':{'manifest':Manifest(branch=linux_branch.GB_HOUSE), 'target_product':target_product.MSM8660_SURF, 'site':test_bed_site.BOULDER, 'prism_target':'MSM8660'},
    'MSM8260.LA.2.0.3.55.3':{'manifest':Manifest(branch=linux_branch.GB_HOUSE), 'target_product':target_product.MSM8660_SURF, 'site':test_bed_site.BOULDER, 'prism_target':'MSM8660'},
    'MSM8660.LA.1.1':{'manifest':Manifest(branch=linux_branch.GB_HOUSE), 'target_product':target_product.MSM8660_SURF, 'site':test_bed_site.BOULDER, 'prism_target':'MSM8660'},
    'MSM8660.LA.1.2':{'manifest':Manifest(branch=linux_branch.GB_REL), 'target_product':target_product.MSM8660_SURF, 'site':test_bed_site.BOULDER, 'prism_target':'MSM8660'},
    'MSM8660.LA.1.0':{'manifest':Manifest(branch=linux_branch.GB_REL), 'target_product':target_product.MSM8660_SURF, 'site':test_bed_site.BOULDER, 'prism_target':'MSM8660'},
    'MSM8655.LA.4.0':{'manifest':Manifest(branch=linux_branch.GB_REL), 'target_product':target_product.MSM7630_SURF, 'site':test_bed_site.BOULDER, 'prism_target':'MSM8655'},
    'MSM8655.LA.3.1':{'manifest':Manifest(branch=linux_branch.GB_REL), 'target_product':target_product.MSM7630_SURF, 'site':test_bed_site.BOULDER, 'prism_target':'MSM8655'},
    'MSM7630.LA.4.11':{'manifest':Manifest(branch=linux_branch.GB_HOUSE), 'target_product':target_product.MSM7630_SURF, 'site':test_bed_site.BOULDER, 'prism_target':'MSM7630.LA'},
    'MSM7630.LA.4.1.3.0.99':{'manifest':Manifest(branch=linux_branch.GB_HOUSE), 'target_product':target_product.MSM7630_SURF, 'site':test_bed_site.BOULDER, 'prism_target':'MSM7630.LA'},
    'MSM7630.LA.4.1':{'manifest':Manifest(branch=linux_branch.GB_HOUSE), 'target_product':target_product.MSM7630_SURF, 'site':test_bed_site.BOULDER, 'prism_target':'MSM7630.LA'},
    'MSM7630.LA.4.0':{'manifest':Manifest(branch=linux_branch.GB_REL), 'target_product':target_product.MSM7630_SURF, 'site':test_bed_site.BOULDER, 'prism_target':'MSM7630.LA'},
    'MSM7630.LA.3.0':{'manifest':Manifest(branch=linux_branch.FY_PUMP), 'target_product':target_product.MSM7630_FUSION, 'site':test_bed_site.BOULDER, 'prism_target':'MSM7630.LA'},
    'MSM7630.LA.2.0.3.8.1':{'manifest':Manifest(branch=linux_branch.FY_STRAW), 'target_product':target_product.MSM7630_SURF, 'site':test_bed_site.BOULDER, 'prism_target':'MSM7630.LA'},
    'MSM7630.LA.2.0.3.20.1':{'manifest':Manifest(branch=linux_branch.FY_STRAW), 'target_product':target_product.MSM7630_SURF, 'site':test_bed_site.BOULDER, 'prism_target':'MSM7630.LA'},
    'MSM7630.LA.2.0.3.10.1':{'manifest':Manifest(branch=linux_branch.FY_STRAW), 'target_product':target_product.MSM7630_SURF, 'site':test_bed_site.BOULDER, 'prism_target':'MSM7630.LA'},
    'MSM7630.LA.2.0.3.0.1':{'manifest':Manifest(branch=linux_branch.FY_STRAW), 'target_product':target_product.MSM7630_SURF, 'site':test_bed_site.BOULDER, 'prism_target':'MSM7630.LA'},
    'MSM7630.LA.2.0':{'manifest':Manifest(branch=linux_branch.FY_PUMP), 'target_product':target_product.MSM7630_SURF, 'site':test_bed_site.BOULDER, 'prism_target':'MSM7630.LA'},
    'MSM7630.LA.1.0':{'manifest':Manifest(branch='eclair_caramel'), 'target_product':target_product.MSM7630_SURF, 'site':test_bed_site.BOULDER, 'prism_target':'MSM7630.LA'},
    'MSM7627A.LA.1.0':{'manifest':Manifest(branch=linux_branch.GB_CHOC), 'target_product':target_product.MSM7627A, 'site':test_bed_site.BOULDER, 'prism_target':'SURF7627A-ANDROID'},
    'MSM7627.LA.7.2':{'manifest':Manifest(branch=linux_branch.GB_HOUSE), 'target_product':target_product.MSM7627_SURF, 'site':test_bed_site.BOULDER, 'prism_target':'SURF7627-ANDROID'},
    'MSM7627.LA.7.1':{'manifest':Manifest(branch=linux_branch.GB_HOUSE), 'target_product':target_product.MSM7627_SURF, 'site':test_bed_site.BOULDER, 'prism_target':'SURF7627-ANDROID'},
    'MSM7627.LA.7.0':{'manifest':Manifest(branch=linux_branch.FY), 'target_product':target_product.MSM7627_SURF, 'site':test_bed_site.BOULDER, 'prism_target':'SURF7627-ANDROID'},
    'MSM7627.LA.6.1':{'manifest':Manifest(branch=linux_branch.GB_REL), 'target_product':target_product.MSM7627_SURF, 'site':test_bed_site.BOULDER, 'prism_target':'SURF7627-ANDROID'},
    'MSM7627.LA.6.0':{'manifest':Manifest(branch=linux_branch.FY_ALMOND), 'target_product':target_product.MSM7627_SURF, 'site':test_bed_site.BOULDER, 'prism_target':'SURF7627-ANDROID'},
    'MSM7627.LA.5.0':{'manifest':Manifest(branch='eclair_chocolate'), 'target_product':target_product.MSM7627_SURF, 'site':test_bed_site.BOULDER, 'prism_target':'SURF7627-ANDROID'},
    'MSM7627.LA.4.0':{'manifest':Manifest(branch='??'), 'target_product':'??', 'site':test_bed_site.BOULDER, 'prism_target':'SURF7627-ANDROID'},
    'MSM7625.LA.2.0':{'manifest':Manifest(branch='??'), 'target_product':'??', 'site':test_bed_site.BOULDER, 'prism_target':'SURF7627-ANDROID'},
  }

  # ADD PSEUDO PL BAIT targets HERE
  # '<PSEUDO_PL_NAME>':{'manifest':Manifest(branch='<manifest_branch>'), 'target_product':'<hardware_target>', 'site':'<site>', 'prism_target':'<prism_target>'},
  _mapping_by_pseudo_pl = {
    'msm7630_gb':{'manifest':Manifest(branch=linux_branch.GB), 'target_product':target_product.MSM7630_SURF, 'site':test_bed_site.BOULDER, 'prism_target':''},
    'msm8660_gb':{'manifest':Manifest(branch=linux_branch.GB), 'target_product':target_product.MSM8660_SURF, 'site':test_bed_site.BOULDER, 'prism_target':''},
    'msm7627_gb':{'manifest':Manifest(branch=linux_branch.GB), 'target_product':target_product.MSM7627_SURF, 'site':test_bed_site.BOULDER, 'prism_target':''},
  }

  _mapping_by_all_pls = {}

  # The pl_type must be a member of PLTypes, and defines whether the instance
  # will reference true PL data, pseudo-PL data or the combination thereof.
  def __init__(self, pl_type):
    assert(pl_type in PLTypes)
    if pl_type == PL:
      self.pl_db = dict(self._mapping_by_pl.items())
    elif pl_type == PSEUDO_PL:
      self.pl_db = dict(self._mapping_by_pseudo_pl.items())
    elif pl_type == ALL_PL:
      self._mapping_by_all_pls = dict(self._mapping_by_pl.items())
      self._mapping_by_all_pls.update(self._mapping_by_pseudo_pl)
      self.pl_db = dict(self._mapping_by_all_pls.items())

    self.pl_mapping_by_manifest = {}
    self.pl_mapping_by_target_product = {}
    self.site_mapping_by_target_manifest = {}
    self._populatePLMappingByManifest()
    self._populateSiteMappingByTargetManifest()
    self._populatePLMappingByTargetProduct()

  def _populatePLMappingByManifest(self):
    if not self.pl_mapping_by_manifest:
      for pl_name, pl_data in self.pl_db.iteritems():
        if pl_data['manifest'] not in self.pl_mapping_by_manifest:
          self.pl_mapping_by_manifest[pl_data['manifest']]={'PLs':[pl_name], 'target_product':[pl_data['target_product']]}
        else:
          self.pl_mapping_by_manifest[pl_data['manifest']]['PLs'].append(pl_name)
          self.pl_mapping_by_manifest[pl_data['manifest']]['target_product'].append(pl_data['target_product'])
    return

  def _populateSiteMappingByTargetManifest(self):
    if not self.site_mapping_by_target_manifest:
      for pl_name, pl_data in self.pl_db.iteritems():
        if pl_data['manifest'] not in self.site_mapping_by_target_manifest:
          self.site_mapping_by_target_manifest[pl_data['manifest']]={'target_site':[pl_data['target_product'] + "@" + pl_data['site']]}
        else:
          self.site_mapping_by_target_manifest[pl_data['manifest']]['target_site'].append(pl_data['target_product'] + "@" + pl_data['site'])
    return

  def _populatePLMappingByTargetProduct(self):
    if not self.pl_mapping_by_target_product:
      for pl_name, pl_data in self.pl_db.iteritems():
        if pl_data['target_product'] not in self.pl_mapping_by_target_product:
          self.pl_mapping_by_target_product[pl_data['target_product']]={'PLs':[pl_name], 'manifests':[pl_data['manifest']]}
        else:
          self.pl_mapping_by_target_product[pl_data['target_product']]['PLs'].append(pl_name)
          self.pl_mapping_by_target_product[pl_data['target_product']]['manifests'].append(pl_data['manifest'])

  # getManifestByPL - returns a string representing the unique manifest associated with a PL
  def getManifestByPL(self, pl):
    if pl in self.pl_db:
      return self.pl_db[pl]['manifest']
    else:
      return 0

  # getTargetByPL - returns a string representing the unique target_product associated with a PL
  def getTargetByPL(self, pl):
    if pl in self.pl_db:
      return self.pl_db[pl]['target_product']
    else:
      return 0

  # getPrismTargetByPL - returns a string representing the unique PRISM target associated with a PL
  def getPrismTargetByPL(self, pl):
    if pl in self.pl_db:
      return self.pl_db[pl]['prism_target']
    else:
      return 0

  # getTargetsByManifest - returns a list of strings representing all targets associated with a manifest
  def getTargetsByManifest(self, manifest):
    if isinstance(manifest, str):
      manifest = Manifest(textual_representation=manifest)
    elif not isinstance(manifest, Manifest):
       raise Exception("Formal parameter 'manifest' must be of type %s or %s." % type(str), type(Manifest))

    if manifest in self.pl_mapping_by_manifest:
      return self.pl_mapping_by_manifest[manifest]['target_product']
    else:
      return 0

  # getTargetsSiteByManifest - returns a list of strings with format 'target@site' associated with a manifest
  def getTargetsSiteByManifest(self, manifest):
    if isinstance(manifest, str):
      manifest = Manifest(textual_representation=manifest)
    elif not isinstance(manifest, Manifest):
      raise Exception("Formal parameter 'manifest' must be of type %s or %s." % type(str), type(Manifest))

    if manifest in self.site_mapping_by_target_manifest:
      return self.site_mapping_by_target_manifest[manifest]['target_site']
    else:
      return 0

  # getPLsByManifest - returns a list of strings representing all PLs associated with a manifest
  def getPLsByManifest(self, manifest):
    if isinstance(manifest, str):
      manifest = Manifest(textual_representation=manifest)
    elif not isinstance(manifest, Manifest):
      raise Exception("Formal parameter 'manifest' must be of type %s or %s." % type(str), type(Manifest))

    if manifest in self.pl_mapping_by_manifest:
      return self.pl_mapping_by_manifest[manifest]['PLs']
    else:
      return 0

  # getManifestsByTarget - returns a list of strings representing all manifests associated with a target
  def getManifestsByTarget(self, target):
    if target in self.pl_mapping_by_target_product:
      return self.pl_mapping_by_target_product[target]['manifests']
    else:
      return 0

  # getPLsByTarget - returns a list of strings representing all PLs associated with a target
  def getPLsByTarget(self, target):
    if target in self.pl_mapping_by_target_product:
      return self.pl_mapping_by_target_product[target]['PLs']
    else:
      return 0


target_product_to_actual_hw = {
  target_product.MSM7630_SURF : [ actual_hardware.MSM8655_SURF, actual_hardware.MSM8655_FFA,
                                  actual_hardware.MSM8655_FLUID, actual_hardware.MSM7630_SURF,
                                  actual_hardware.MSM7630_FFA, actual_hardware.MSM7630_FLUID,
                                ],
  target_product.MSM7630_FUSION : [ actual_hardware.MSM8655_SURF, actual_hardware.MSM8655_FFA,
                                  ],
  target_product.MSM8660_SURF : [ actual_hardware.MSM8660_SURF, actual_hardware.MSM8660_FFA,
                                  actual_hardware.MSM8660_FLUID
                                ],
  target_product.MSM7627_SURF : [ actual_hardware.MSM7627_SURF, actual_hardware.MSM7627_FFA,
                                ],
  target_product.MSM7625_SURF : [ actual_hardware.MSM7625_SURF,
                                ],
  target_product.MSM7627A : [ actual_hardware.MSM7627A_SURF,
                            ],
  target_product.MSM8960 : [ actual_hardware.MSM8960_CDP, actual_hardware.MSM8960_MTP,
                             actual_hardware.MSM8960_FLUID,
                           ],
}

# getActualHW - returns a list of strings representing the automation "actual
#   hardware" values for a target product
def getActualHW(target):
  if target in target_product_to_actual_hw:
    return target_product_to_actual_hw[target]
  else:
    return 0

if __name__ == '__main__':
  parser = OptionParser()
  parser.add_option("--get", default="PLs", help="One of 'PLs', 'targets', 'manifests', 'targets_and_sites', or 'hardware'")
  parser.add_option("--from", dest='argtype', default="manifest", help ="One of 'PL', 'target', or 'manifest'")
  parser.set_usage("%prog --get=<get_type> --from=<from_type> key... \n\n"
                   "NOTE: the get_type 'hardware' only supports the from_type "
                   "target. Specifying a get_type and from_type that refer to "
                   "the same field is not allowed.")
  (options, args) = parser.parse_args()

  if options.get.startswith(options.argtype):
    sys.stderr.write("--get and --from must refer to different fields.")
    sys.exit(1)

  # Create a PLMap to service the command-line query
  query_pl_map = PLMap(PL)

  # Choosing which query function to use.
  if options.get == 'hardware':
    if options.argtype == 'target':
      command=globals()['getActualHW']
    else:
      sys.stderr.write("--get=hardware is only supported with --from=target")
      sys.exit(1)
  elif options.get == 'PLs':
    if options.argtype == 'target':
      command=query_pl_map.getPLsByTarget
    elif options.argtype == 'manifest':
      command=query_pl_map.getPLsByManifest
    else:
      sys.stderr.write("Unrecognized 'from' option. Please choose one of 'target' or 'manifest'")
      sys.exit(1)
  elif options.get == 'targets':
    if options.argtype == 'PL':
      command = query_pl_map.getTargetByPL
    elif options.argtype == 'manifest':
      command = query_pl_map.getTargetsByManifest
    else:
      sys.stderr.write("Unrecognized 'from' option. Please choose one of 'pl' or 'manifest'")
      sys.exit(1)
  elif options.get == 'targets_and_sites':
    if options.argtype == 'manifest':
      command = query_pl_map.getTargetsSiteByManifest
    else:
      sys.stderr.write("Unrecognized 'from' option. Please choose 'manifest'")
      sys.exit(1)
  elif options.get == 'manifests':
    if options.argtype == 'target':
      command = query_pl_map.getManifestsByTarget
    elif options.argtype == 'PL':
      command = query_pl_map.getManifestByPL
    else:
      sys.stderr.write("Unrecognized 'from' option. Please choose one of 'target' or 'PL'")
      sys.exit(1)
  else:
    sys.stderr.write("Unrecognized 'get' option. Please choose one of 'PLs', 'targets', 'manifests', or 'hardware'.")
    sys.exit(1)

  for arg in args:
    result = command(arg)
    if result:
      if isinstance(result, str) or isinstance(result, Manifest):
        print result
      else:
        result = sorted(set(result))
        output = ''
        for i in range(len(result) - 1):
          output += str(result[i]) + ','

        if len(result) > 0:
          output += str(result[len(result) - 1])
        print output
