#!/usr/bin/env python

# Copyright (c) 2011 QUALCOMM Incorporated.  All Rights Reserved.
# QUALCOMM Proprietary and Confidential.

# This module provides class-based interfaces for enumerating and
# validating values used in BAIT (e.g. branches, target products,
# actual hardware, test-bed sites, etc).

class validation_list(object):
  def __init__(self, init_list):
    self._canon_list = frozenset(init_list)

  def __iter__(self):
    return iter(self._canon_list)

  def check(self, value):
    return value in self._canon_list

class linux_branch(validation_list):
# Linux project branch values
  FY = 'froyo'
  FY_ALMOND = 'froyo_almond'
  FY_STRAW = 'froyo_strawberry'
  FY_PUMP = 'froyo_pumpkin'
  GB = 'gingerbread'
  GB_HOUSE = 'gingerbread_house'
  GB_REL = 'gingerbread_rel'
  GB_CHOC = 'gingerbread_chocolate'
  HC = 'honeycomb'
  HC_MR1 = 'honeycomb_mr1'
  HC_MR2 = 'honeycomb_mr2'

  def __init__(self):
    _linux_branch_values = [self.FY,  self.FY_ALMOND, self.FY_STRAW,
                            self.FY_PUMP,
                            self.GB, self.GB_HOUSE, self.GB_REL, self.GB_CHOC,
                            self.HC, self.HC_MR1, self.HC_MR2
                           ]
    validation_list.__init__(self, _linux_branch_values)

class target_product(validation_list):
# Target product values
  EM = 'emulator'
  MSM7630_SURF = 'msm7630_surf'
  MSM7630_FUSION = 'msm7630_fusion'
  MSM8660_SURF = 'msm8660_surf'
  MSM8660_CSFB = 'msm8660_csfb'
  MSM8660_SVLTE = 'msm8660_svlte'
  MSM7627_SURF = 'msm7627_surf'
  MSM7625_SURF = 'msm7625_surf'
  MSM7627A = 'msm7627a'
  QSD8650_FFA = 'qsd8650_ffa'
  QSD8650_SURF = 'qsd8650_surf'
  MSM8650A_ST1X = 'qsd8650a_st1x'
  MSM8960 = 'msm8960'

  def __init__(self):
    _target_product_values = [self.EM, self.MSM7630_SURF, self.MSM7630_FUSION,
                              self.MSM8660_CSFB, self.MSM8660_SVLTE,
                              self.MSM7627_FFA, self.MSM7627_SURF,
                              self.MSM7625_SURF, self.MSM7627A,
                              self.QSD8650_FFA, self.QSD8650_SURF,
                              self.MSM8650A_ST1X,
                              self.MSM8960
                             ]
    validation_list.__init__(self, _target_product_values)


# Actual hardware values; these represent the hardware variants for
# target_products.  Typically, a single target_product will correspond to
# multiple actual_hardware values.
# TODO: Do we need 8650 to be MSM, or QSD?
# TODO: Likewise for 8650A
# TODO: Eliminated Virtio platform for 8960, is that okay?
class actual_hardware(validation_list):
  EM = 'Emulator'
  MSM8655_SURF = 'msm8655_surf'
  MSM8655_FFA = 'msm8655_ffa'
  MSM8655_FLUID = 'msm8655_fluid'
  MSM7630_FFA = 'msm7630_ffa'
  MSM7630_SURF = 'msm7630_surf'
  MSM7630_FLUID = 'msm7630_fluid'
  MSM8660_SURF = 'msm8660_surf'
  MSM8660_FFA = 'msm8660_ffa'
  MSM8660_FLUID = 'msm8660_fluid'
  MSM8660_CSFB = 'msm8660_csfb'
  MSM8660_SVLTE = 'msm8660_svlte'
  MSM7627_FFA = 'msm7627_ffa'
  MSM7627_SURF = 'msm7627_surf'
  MSM7625_SURF = 'msm7625_surf'
  MSM7627A_SURF = 'msm7627a_surf'
  MSM7627A_FFA = 'msm7627a_ffa'
  MSM8650_FFA = 'msm8650_ffa'
  MSM8650_SURF = 'msm8650_surf'
  MSM8650A_ST1X = 'msm8650a_st1x'
  MSM8960_CDP = 'msm8960_cdp'
  MSM8960_MTP = 'msm8960_mtp'
  MSM8960_FLUID = 'msm8960_fluid'

  def __init__(self):
    _actual_hardware_values = [self.EM,
                               self.MSM8655_SURF, self.MSM8655_FFA,
                               self.MSM8655_FLUID,
                               self.MSM7630_FFA, self.MSM7630_FLUID,
                               self.MSM8660_SURF, self.MSM8660_FFA,
                               self.MSM8660_FLUID,
                               self.MSM8660_CSFB, self.MSM8660_SVLTE,
                               self.MSM7627_FFA, self.MSM7627_SURF,
                               self.MSM7625_SURF, self.MSM7627A_SURF,
                               self.MSM7627A_FFA,
                               self.MSM8650_FFA, self.MSM8650_SURF,
                               self.MSM8650A_ST1X,
                               self.MSM8960_CDP, self.MSM8960_MTP,
                               self.MSM8960_FLUID
                              ]
    validation_list.__init__(self, _actual_hardware_values)

class test_bed_site(validation_list):
  """Linux project test-bed site values"""
  BOULDER = 'boulder'
  HYDERABAD = 'hyderabad'
  SAN_DIEGO = 'sandiego'
  NEW_JERSEY = 'bridgewater'

  def __init__(self):
    _linux_testbed_site_values = [self.BOULDER,
                                  self.HYDERABAD,
                                  self.SAN_DIEGO,
                                  self.NEW_JERSEY
                                 ]
    validation_list.__init__(self, _linux_testbed_site_values)

