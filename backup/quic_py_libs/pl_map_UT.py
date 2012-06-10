#!/usr/bin/env python

# Copyright (c) 2011 QUALCOMM Incorporated.  All Rights Reserved.
# QUALCOMM Proprietary and Confidential.

import sys

#Local imports
import pl_map
from manifest_repr import Manifest

test_pl="MSM8960.LA.1.0"
test_manifest="git.quicinc.com/platform/manifest:gingerbread"
test_target="msm8960"
test_garbage="garbage"

pl_ut = pl_map.PLMap(pl_map.PL)

if Manifest(textual_representation=test_manifest) != pl_ut.getManifestByPL(test_pl):
  print "FAIL: getManifestByPL(%s)" % test_pl
  sys.exit(0)
if test_target not in pl_ut.getTargetByPL(test_pl):
  print "FAIL: getTargetByPL(%s)" % test_pl
  sys.exit(0)
if test_target not in pl_ut.getTargetsByManifest(test_manifest):
  print "FAIL: getTargetsByManifest(%s)" % test_manifest
  sys.exit(0)
if test_pl not in pl_ut.getPLsByManifest(test_manifest):
  print "FAIL: getPLsByManifest(%s)" % test_manifest
  sys.exit(0)
if Manifest(textual_representation=test_manifest) not in pl_ut.getManifestsByTarget(test_target):
  print "FAIL: getManifestsByTarget(%s)" % test_target
  sys.exit(0)
if test_pl not in pl_ut.getPLsByTarget(test_target):
  print "FAIL: getPLsByTarget(%s)" % test_target
  sys.exit(0)
if not pl_map.getActualHW(test_target):
  print "FAIL: getActualHW(%s)" % test_target
  sys.exit(0)

if pl_ut.getManifestByPL(test_garbage):
  print "FAIL: getManifestByPL(%s)" % test_garbage
  sys.exit(0)
if pl_ut.getTargetByPL(test_garbage):
  print "FAIL: getTargetByPL(%s)" % test_garbage
  sys.exit(0)

try:
  if pl_ut.getTargetsByManifest(test_garbage):
    print "FAIL: getTargetsByManifest(%s)" % test_garbage
    sys.exit(0)
except Exception as e:
  print e

try:
  if pl_ut.getPLsByManifest(test_garbage):
    print "FAIL: getPLsByManifest(%s)" % test_garbage
    sys.exit(0)
except Exception as e:
  print e

if pl_ut.getManifestsByTarget(test_garbage):
  print "FAIL: getManifestsByTarget(%s)" % test_garbage
  sys.exit(0)
if pl_ut.getPLsByTarget(test_garbage):
  print "FAIL: getPLsByTarget(%s)" % test_garbage
  sys.exit(0)
if pl_map.getActualHW(test_garbage):
  print "FAIL: getActualHW(%s)" % test_garbage
  sys.exit(0)

print "PASS\n"
sys.exit(0)
