#!/usr/bin/env python2.6

import os
import subprocess

class ElectricCommander:
  def __init__(self, sessionId, server="commander.qualcomm.com"):
    self.server = server
    self.sessionId = sessionId

  def getProperty(self, propertyName):
    command = ['ectool', '--server', self.server, 'getProperty', propertyName]
    new_env = os.environ.copy()
    new_env['COMMANDER_SESSIONID'] = self.sessionId
    process = subprocess.Popen(command, env=new_env,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    std_out, std_err = process.communicate()
    return std_out, std_err

  def setProperty(self, propertyName, value):
    command = ['ectool', '--server', self.server, 'setProperty',
               propertyName, value]
    new_env = os.environ.copy()
    new_env['COMMANDER_SESSIONID'] = self.sessionId
    process = subprocess.Popen(command, env=new_env,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    std_out, std_err = process.communicate()
    return std_out, std_err

  def runProcedure(self, project, procedure, **kwargs):
    command = ['ectool', '--server', self.server, 'runProcedure', project,
               '--procedureName', procedure]
    if kwargs:
      command.append('--actualParameter')
      for key, value in kwargs.iteritems():
        command.append('%s=%s' % (key, value))

    new_env = os.environ.copy()
    new_env['COMMANDER_SESSIONID'] = self.sessionId
    process = subprocess.Popen(command, env=new_env,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    std_out, std_err = process.communicate()
    print std_out
    print std_err
    return std_out
