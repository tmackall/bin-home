#!/usr/bin/env python2.6

import sys
import common

def invoke_CheckCall(cmd1):
  try:
    (cmd_out, cmd_err) = common.CheckCall(cmd1)

    print " ".join(cmd1)
    print "stdout\n" + cmd_out
    print "stderr\n" + cmd_err
  except common.CheckCallError, e:
    print e

def invoke_CheckCallWithPipe(cmd1, cmd2):
  try:
    (cmd_out, cmd_err) = common.CheckCallWithPipe(cmd1, cmd2)

    command = "%s | " % " ".join(cmd1)
    command += " ".join(cmd2)
    print command
    print "stdout\n" + cmd_out
    print "stderr\n" + cmd_err
  except common.CheckCallError, e:
    print e

def test_CheckCall():
  print "test_CheckCall"
  print "case1: fail cmd1"
  cmd1 = ['cat', '/usr/include/xyz.h']
  invoke_CheckCall(cmd1)

  print "case2: pass cmd1"
  cmd1 = ['ls', '-x']
  invoke_CheckCall(cmd1)

def test_CheckCallWithPipe():
  print "test_CheckCallWithPipe"
  # fail cmd1
  print "case1: fail cmd1"
  cmd1 = ['cat', '/usr/include/xyz.h']
  cmd2 = ['grep', 'typedef']
  invoke_CheckCallWithPipe(cmd1, cmd2)

  # fail cmd2
  print "case2: fail cmd2"
  cmd1 = ['cat', '/usr/include/stdint.h']
  cmd2 = ['xargs', 'sort']
  invoke_CheckCallWithPipe(cmd1, cmd2)

  print "case3: pass cmd1, cmd2"
  cmd1 = ['cat', '/usr/include/stdint.h']
  cmd2 = ['grep', 'typedef']
  invoke_CheckCallWithPipe(cmd1, cmd2)

def main(argv):

  print '--------'
  test_CheckCall()
  print '--------'
  test_CheckCallWithPipe()
  print '--------'

if __name__ == '__main__':
  main(sys.argv)
