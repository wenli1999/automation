# Name: snmpbulkwalk_3walks.py
#
# Description:
# - Not O-O yet
# - Commands: snmpbulkwalk -v2c -t 15 -c public 10.10.232.46 1.3.6.1.4.1.6141.2.60

progName = 'snmpbulkwalk_3walks.py'

import sys
import time
import pexpect
from subprocess import Popen, PIPE

def formattedHdr(f, msg):	
	currDT = getCurrentDT()
	tmpStr = '='*66 + '\n' + '='*15 + ' current-date-time = ' + currDT + ' ' + '='*15 + '\n'
	f.write(tmpStr)
	print tmpStr
	f.write(msg + '\n')
	print msg
	
def getCurrentDT():
	dt = time.localtime()
	dtFormatted  = str(dt.tm_year)+str(dt.tm_mon).zfill(2)+str(dt.tm_mday).zfill(2)
	dtFormatted += str(dt.tm_hour).zfill(2)+str(dt.tm_min).zfill(2)+str(dt.tm_sec).zfill(2)
	return dtFormatted
	
def startTelnetSession(ip, prompt, login, password):
	print "Spawning a telnet session ..."
	print("Creating telnet session with,\n\nip=%s  prompt=%s  login=%s  password=%s\n") % (ip, prompt, login, password)
	spawnParam='telnet ' + ip
	spawnId = pexpect.spawn(spawnParam)
	spawnId.expect('login:')
	spawnId.sendline(login)
	print "-------------- after gss ---------"
	spawnId.expect('Password:')
	spawnId.sendline(password)
	print "-------------- after password ---------"
	spawnId.expect(prompt)	
	return spawnId

def sendCommand(sessId, command, prompt, tOut=None):
	if tOut == None:
		sendCmdTimeout = 30
	else:
		sendCmdTimeout = tOut
		
	sessId.sendline(command)
	sessId.expect(prompt, timeout=sendCmdTimeout)
	print "====>>> p.before"
	print sessId.before
	print "====>>> p.after"
	print sessId.after
	return sessId.before			

# The preceding 1.3.6.1.4.1 is stripped in the actual returned from asnmpbulkwalk 
oid_CpuUtilLast05SecondsCur = '6141.2.60.12.1.11.1.0'
oid_CpuUtilLast05SecondsMin = '6141.2.60.12.1.11.2.0'
oid_CpuUtilLast05SecondsMax = '6141.2.60.12.1.11.3.0'

oid_CpuUtilLast10SecondsCur = '6141.2.60.12.1.11.5.0'
oid_CpuUtilLast10SecondsMin = '6141.2.60.12.1.11.6.0'
oid_CpuUtilLast10SecondsMax = '6141.2.60.12.1.11.7.0'

oid_CpuUtilLast60SecondsCur = '6141.2.60.12.1.11.9.0'
oid_CpuUtilLast60SecondsMin = '6141.2.60.12.1.11.10.0'
oid_CpuUtilLast60SecondsMax = '6141.2.60.12.1.11.11.0'

oid_FileSysUtilTmpFsCur 	= '6141.2.60.12.1.12.1.0'
oid_FileSysUtilTmpFsMin 	= '6141.2.60.12.1.12.2.0'
oid_FileSysUtilTmpFsMax 	= '6141.2.60.12.1.12.3.0'

oid_FileSysUtilSysFsCur 	= '6141.2.60.12.1.12.5.0'
oid_FileSysUtilSysFsMin 	= '6141.2.60.12.1.12.6.0'
oid_FileSysUtilSysFsMax 	= '6141.2.60.12.1.12.7.0'

oid_FileSysUtilXftpCur 		= '6141.2.60.12.1.12.9.0'
oid_FileSysUtilXftpMin 		= '6141.2.60.12.1.12.10.0'
oid_FileSysUtilXftpMax 		= '6141.2.60.12.1.12.11.0'

oid_MemUtilUsedMemCur 		= '6141.2.60.12.1.13.1.0'
oid_MemUtilUsedMemMin 		= '6141.2.60.12.1.13.2.0'
oid_MemUtilUsedMemMax 		= '6141.2.60.12.1.13.3.0'

oid_MemUtilAvailMemCur 		= '6141.2.60.12.1.13.4.0'
oid_MemUtilAvailMemMin 		= '6141.2.60.12.1.13.5.0'
oid_MemUtilAvailMemMax 		= '6141.2.60.12.1.13.6.0'

# appending header to be used by excel graphing
dataCollected = { 	oid_CpuUtilLast05SecondsCur : 'oid_CpuUtilLast05SecondsCur',
					oid_CpuUtilLast05SecondsMin : 'oid_CpuUtilLast05SecondsMin',
					oid_CpuUtilLast05SecondsMax : 'oid_CpuUtilLast05SecondsMax',
					
					oid_CpuUtilLast10SecondsCur : 'oid_CpuUtilLast10SecondsCur',
					oid_CpuUtilLast10SecondsMin : 'oid_CpuUtilLast10SecondsMin',
					oid_CpuUtilLast10SecondsMax : 'oid_CpuUtilLast10SecondsMax',
					
					oid_CpuUtilLast60SecondsCur : 'oid_CpuUtilLast60SecondsCur',
					oid_CpuUtilLast60SecondsMin : 'oid_CpuUtilLast60SecondsMin',
					oid_CpuUtilLast60SecondsMax : 'oid_CpuUtilLast60SecondsMax',

					oid_FileSysUtilTmpFsCur 	: 'oid_FileSysUtilTmpFsCur',
					oid_FileSysUtilTmpFsMin 	: 'oid_FileSysUtilTmpFsMin',
					oid_FileSysUtilTmpFsMax 	: 'oid_FileSysUtilTmpFsMax',

					oid_FileSysUtilSysFsCur 	: 'oid_FileSysUtilSysFsCur',
					oid_FileSysUtilSysFsMin 	: 'oid_FileSysUtilSysFsMin',
					oid_FileSysUtilSysFsMax 	: 'oid_FileSysUtilSysFsMax',

					oid_FileSysUtilXftpCur 		: 'oid_FileSysUtilXftpCur',
					oid_FileSysUtilXftpMin 		: 'oid_FileSysUtilXftpMin',
					oid_FileSysUtilXftpMax 		: 'oid_FileSysUtilXftpMax',
					
					oid_MemUtilUsedMemCur 		: 'oid_MemUtilUsedMemCur',
					oid_MemUtilUsedMemMin 		: 'oid_MemUtilUsedMemMin',
					oid_MemUtilUsedMemMax 		: 'oid_MemUtilUsedMemMax',

					oid_MemUtilAvailMemCur 		: 'oid_MemUtilAvailMemCur',
					oid_MemUtilAvailMemMin 		: 'oid_MemUtilAvailMemMin',
					oid_MemUtilAvailMemMax 		: 'oid_MemUtilAvailMemMax'
				}	

tmp = sys.argv

if len(tmp) == 4:
	snmpIP	 = tmp[1]
	walkMax  = tmp[2]
	walkWait = tmp[3]
else:
	print '\n\n\nAbort!!!'
	print "%s:  The 3 parameters are walk-ip-address  walk-max-count  wait-before-next-walk-in-seconds\n\n\n" % (progName)
	sys.exit(-1)
	
# snmpIP = '10.10.232.46' 
# walkMax   = 3
# creating all-capture log file

currDT = getCurrentDT()
logWalkFileName = progName + '_' + 'captureLog' '_' + currDT
f = open(logWalkFileName, 'w')

startTime = time.localtime() 
csvFileName = logWalkFileName + '.csv'

for walkCnt in range(1, int(walkMax)+1):
	formattedHdr(f, 'start snmpbulkwalk capture ...' + ' (walkCount=' + str(walkCnt) + ')')
	cmd_snmpbulkwalk = 'snmpbulkwalk -v 2c -t 30 -r 3 -c public ' + snmpIP + ' 1.3.6.1.4.1.6141.2.60'
	p = Popen(cmd_snmpbulkwalk , shell=True, stdout=PIPE, stderr=PIPE)
	output, err = p.communicate()
	formattedHdr(f, 'end snmpbulkwalk capture.' + ' (walkCount=' + str(walkCnt) + ')')
	
	walkFailCnt = []		# a list to keep track of where walks fail to generate require data
	# Warning:  The line values returned from walk is very context sensitive
	k = 0
	noFailInAWalk = True				
	for aLine in output.split('\n'):
		#print "--aLine--> ", aLine
		k += 1
		for i, j in dataCollected.iteritems():
			dum = aLine.split(' ')
			if len(dum) == 4:  #This is context detection
				retOid   = dum[0].split('enterprises.')[1]
				retValue = dum[3]
				if i == retOid:
					#print "************** >>>retValues:", retOid, retValue
					noFailInAWalk = False
					dataCollected[i] = j + ', ' + retValue
					#print ('lineNum=%s:  i=%s ==>> j=%s dataCollected[i]=%s') % (k, i, j, dataCollected[i])
	if noFailInAWalk == True:
		walkFailCnt.append(k)
	# all captured data
	f.write(output)
	
	# targetted data for graphing in csv format
	# File over-write after every walk
	#
	# will change to less frequent over-write later
	
	f_csv = open(csvFileName, 'w')
	for key in dataCollected:
		f_csv.write(dataCollected[key] + '\n')	
	f_csv.close()
	
	# display results.
	print "\n\n\n=== searching done, display results.===\n"
	print "The snmpbulkwalk failures count=", len(walkFailCnt)
	print "The snmpbulkwalk failed at counters=", walkFailCnt
	for i, j in dataCollected.iteritems():
		print ('i=%s --> j-%s') % (i, j)

	formattedHdr(f, 'end serching for targetted OIDs' + ' (walkCount=' + str(walkCnt) + ')')				
	f.flush() 		# save intermediate data
	
	time.sleep(float(walkWait))	# time delaybetween each bulk walk

tmpStr = 'end ' + progName + '\n'
formattedHdr(f, tmpStr)	
f.close()

sys.exit(0)

