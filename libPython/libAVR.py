#!/usr/bin/env python2.7
import subprocess
from subprocess import check_call
import os
import re
import time
import logging

AUDIO_SYSTEM_COMMANDS=[ ('1','On'), ('2','Off'), ('3','Reboot'),]
INFO_TYPE=[ (0,'INFO'), (1,'ERROR'),(2,'WARNING')]
gPPS='/home/tmackall/bin/managePPS.exp'
gDenonScript='/home/tmackall/bin/sendAVCommand.sh'
gDenonAV='192.168.1.4'

def readFile (inFile):
    text=''
    # read the file in
    try:
        file = open(inFile,'r')
    except:
        logging.warning('Failed to open file: ' + inFile)
        return 1, text
    try:
        text = file.read()
    except:
        logging.warning ('Failed to read file: %s' % inFile)
        return 2, text
    file.close()
    return  0,text

def execAVRCmd(inCmd):
    logging.debug('execAVRCmd: %s' % inCmd)
    fn='/tmp/t'
    shellCommand='%s %s %s %s' % (gDenonScript,gDenonAV,inCmd,fn)
    for i in range(5):
        try:
            status = check_call(shellCommand,shell=True)
            if status == 0:
                break
        except:
            logging.warning('Failed %s command' % shellCommand)
            status=2
        time.sleep(1)
    if status != 0:
        logging.error('Failed system cmd \(%s\) failed: %s' % \
            (shellCmd,status))
        return 1,''
    status,output=readFile(fn)
    if status != 0:
        logging.error('readFile returned: %s' % status)
        return 1,''
    os.unlink(fn)
    logging.info ('Command Status: %s' % output)
    return 0,output

def getZone2Status():
    logging.debug('getZone2Status' )
    retState=''
    retVol=''
    retSource=''
    status,text=execAVRCmd('Z2?')
    if status != 0:
        logging.error('execAVRCmd returned: %s' % status)
    lText=text.split('\n')
    output=''
    for i in lText:
        logging.debug(i)
        m = re.search(r'.*# (.*)$', i)    
        if m:
            output+=m.group(1)
            logging.debug(output)
    if output == '':
        logging.warning('No output received from receiver')
        return 1,retState,retSource,retVol
    lOutput=output.split('.')
    m=re.search(r'Z2(.*)',lOutput[1])
    retState=m.group(1)
    m=re.search(r'Z2(.*)',lOutput[2])
    retSource=m.group(1)
    m=re.search(r'Z2(.*)',lOutput[3])
    retVol=m.group(1)
    return 0,retState,retSource,retVol

def convertVolToDB(inVol):
    logging.debug('convertVolToDB: %s' % inVol)
    retDB=''
    try:
        realDB=-80 + int(inVol)
    except:
        return 1,retDB

    return 0,str(realDB)
    
