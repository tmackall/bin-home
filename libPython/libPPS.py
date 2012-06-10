from subprocess import call
import time

AUDIO_SYSTEM_COMMANDS=[ ('1','On'), ('2','Off'), ('3','Reboot'),]
INFO_TYPE=[ (0,'INFO'), (1,'ERROR'),(2,'WARNING')]
gPPS='/home/tmackall/bin/managePPS.exp'
gDenonAV='/home/tmackall/bin/sendAVCommand.sh'


def logInfo (infoType, infoData):
	myDict=dict(INFO_TYPE)
	try:
		msgType=myDict[infoType]
	except:
		print "WARNING: Could not map " + str(infoType)
		infoType=1
		msgType=myDict[infoType]
	print msgType + ": " + str(infoData)


def getDeviceState (device):
	global gPPS
	#
	# determine if the amp and AV are already in the requested state
	shellCommand = gPPS + ' get ' +  device
	state = call(shellCommand, shell=True)
	return state

def execPPSCmd (cmd, port, value):
	shellCommand = '/home/tmackall/bin/managePPS.exp ' + cmd +  ' ' +\
		str(port) + ' ' + str(value)
	logInfo (0, "execPPSCmd command: " + shellCommand)
	return call(shellCommand, shell=True)

def hwAudio (avPPS, ampPPS, avIP, command):
	global gPPS
	global gDenonAV
	retStatus=0
	y=dict(AUDIO_SYSTEM_COMMANDS)
	tCommand=y[str(command)]
	avState=getDeviceState (str(avPPS))
	logInfo (0,"AV Current State: " + y[str(avState)])
	ampState=getDeviceState (str(ampPPS))
	logInfo (0,"Amp Current State: " + y[str(ampState)])
	logInfo (0,"Command to exectute: " + tCommand)
	logInfo (0, str(ampState) + " " + str(avState) + " " + str(command))

	
	#
	# see if the AMP and receiver are already in the requested state
	# return immediately if so unless we are rebooting
	if int(avState) != int(command) or \
		int(ampState) != int(command) or command == '3':
		
		# if reboot, power amp and AV off
		if command == '3':
			tCommand == 'Off'
			logInfo (0, "processing force off")
		#
		# turn on/off AV receiver
		if 0 != execPPSCmd ('set', avPPS, tCommand):
			return retStatus
		#
		# turn on/off Knoll amp
		if 0 != execPPSCmd ('set', ampPPS, tCommand):
			return retStatus
		
		#
		# this section is used for reboot
		if command == '3':
			tCommand == 'On'
			time.sleep(45)
			#
			# turn on/off AV receiver
			if 0 != execPPSCmd ('set', avPPS, tCommand):
				return retStatus
			#
			# turn on/off Knoll amp
			if 0 != execPPSCmd ('set', ampPPS, tCommand):
				return retStatus
	else:
		logInfo (retStatus,"Already in the same state")
		return retStatus
		
	#
	# wait for the AV receiver to come up
	if tCommand == 'On' or tCommand ==  'Reboot':
		logInfo (retStatus, "Wait for receiver to come back up.")
		#
		# ping the AV server until it responds or times out
		iterations=6
		maxTime=60
		cnt=iterations	
		while True:
			shellCommand =  'ping -c 1  ' + avIP 
			retStatus = call(shellCommand, shell=True)
			if retStatus == 0: 
				break
			time.sleep(maxTime/iterations)
			cnt -= 1
			if cnt  == 0: 
				retStatus=127
				logInfo (retStatus, "Timeout waiting for AV receiver to come up")
				break
		if retStatus != 0:
			return retStatus

		#
		# turn the main zone off
		time.sleep(1)
		shellCommand = '/home/tmackall/bin/sendAVCommand.sh ' + \
			 str(avIP) + ' ZMOFF' 
		retStatus = call(shellCommand, shell=True)
		logInfo (retStatus,"Turning main zone off")
		if retStatus != 0:
			return retStatus
		
		#
		# turn the volume down for Zone 2
		time.sleep(1)
		shellCommand = '/home/tmackall/bin/sendAVCommand.sh ' + \
			 str(avIP) + ' Z230' 
		retStatus = call(shellCommand, shell=True)
		logInfo (retStatus, "Setting Zone 2 volume")
		if retStatus != 0:
			return retStatus

		#
		# turn on the knoll amp
		shellCommand = '/home/tmackall/bin/managePPS.exp set ' + \
  			str(ampPPS) + ' ' + str(tCommand)
		retStatus = call(shellCommand, shell=True)
		logInfo (retStatus, "Turning on the knoll amp")
		if retStatus != 0:
			return retStatus
	else:
		#
		# for off, delay 1 min		
		logInfo (0, "Sleeping for 1 min on off")
		time.sleep(30)
		logInfo (0, "Done Sleeping")
	return retStatus


