# Upload hex file to Arduboy

#requires pyserial to be installed

import sys
import time
import os
import subprocess
from serial.tools.list_ports  import comports
from serial import Serial
import zipfile

compatibledevices = [
 #Arduino Leonardo
 "VID:PID=2341:0036", "VID:PID=2341:8036",
 "VID:PID=2A03:0036", "VID:PID=2A03:8036",
 #Arduino Micro
 "VID:PID=2341:0037", "VID:PID=2341:8037",
 "VID:PID=2A03:0037", "VID:PID=2A03:8037",
 #Genuino Micro
 "VID:PID=2341:0237", "VID:PID=2341:8237",
 #Sparkfun Pro Micro 5V
 "VID:PID=1B4F:9205", "VID:PID=1B4F:9206",
]

def	getComPort(verbose):
	devicelist = list(comports())
	for device in devicelist:
		for vidpid in compatibledevices:
			if  vidpid in device[2]:
				port=device[0]
				if verbose : print "found {} at port {}".format(device[1],port)
				return port
	if verbose : print "Arduino board not found."

path = os.path.dirname(sys.argv[0])	+ "\\"

#test file exists
if len(sys.argv) <> 2:
	print "USAGE uploader.py filename.hex"
	exit()
filename = sys.argv[1]	
if not os.path.isfile(filename) :
	print "File not found. [{}]".format(filename)
	exit()
	
#if file is zipfile, extract hex file
try:
	zip = zipfile.ZipFile(filename)
	for file in zip.namelist():
		if file.lower().endswith('.hex'):
				zipinfo = zip.getinfo(file)
				zipinfo.filename = "uploader-temp.hex"
				zip.extract(zipinfo,path)
				filename = path + zipinfo.filename;
	tempfile = True
except:
	tempfile = False
	
#trigger bootloader reset
port = getComPort(True)
if port is None :
	sys.exit()
com = Serial(port,1200)
com.close()

#wait for Arduino board to disconnect and reconnect in bootloader mode
while getComPort(False) == port :
	time.sleep(0.1)
while getComPort(False) is None :
	time.sleep(0.1)
port = getComPort(True)

#launch avrdude
avrdude = "{}avrdude.exe".format(path)
config  = "-C{}avrdude.conf".format(path)
subprocess.call ([avrdude,config, "-v", "-patmega32u4", "-cavr109", "-P{}".format(port), "-b57600", "-D", "-Uflash:w:{}:i".format(filename)])
if tempfile == True : os.remove(filename)
time.sleep(5)
#raw_input()