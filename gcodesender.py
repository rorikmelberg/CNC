#!/usr/bin/python
"""\
Simple g-code streaming script
"""
 
import serial
import time
import argparse

# parser = argparse.ArgumentParser(description='This is a basic gcode sender. http://crcibernetica.com')
# parser.add_argument('-p','--port',help='Input USB port',required=True)
# parser.add_argument('-f','--file',help='Gcode file name',required=True)
# args = parser.parse_args()

# argPort = args.port
# argFile = args.file

argPort = 'COM3'
argFile = r"G:\My Drive\Roriks Documents\Projects\CNC-Drawing\Apollo\apollo.gcode"


## show values ##
print ("USB Port: %s" % argPort )
print ("Gcode file: %s" % argFile )


def removeComment(string):
	if (string.find(';')==-1):
		return string
	else:
		return string[:string.index(';')]


def sendLine(s, line):
    msg = (line + '\n').encode('utf-8')
    s.write(msg) # Send g-code block
    grbl_out = s.readline() # Wait for response with carriage return
    print('{} : {}'.format(msg, grbl_out.strip()))
 
def plunge(s):
    sendLine(s,'M5')

def retract(s):
    sendLine(s,'M3S90')
    time.sleep(0.3)

# Open serial port
#s = serial.Serial('/dev/ttyACM0',115200)
s = serial.Serial(argPort, 115200)
print('Opening Serial Port')
 
# Open g-code file
f = open(argFile,'r')
print('Opening gcode file')

# Wake up 
sendLine(s, '\r\n\r\n')
time.sleep(2)   # Wait for Printrbot to initialize
s.flushInput()  # Flush startup text in serial input

# Zero
print('Zeroing Home')
sendLine(s, '$H')
sendLine(s, 'G92 X0 Y0 Z0')
retract(s)

print('Sending gcode')
# Stream g-code
skipNext = False

for line in f:
    if skipNext:
        skipNext = False
        continue 

    if line.lower().strip() == '; plunge':
        plunge(s)
        skipNext = True
        continue

    if line.lower().strip() == '; retract':
        retract(s)
        skipNext = True
        continue

    l = removeComment(line)
    l = l.strip() # Strip all EOL characters for streaming
    if  (l.isspace()==False and len(l)>0) :
        sendLine(s, l)

# Close file and serial port
f.close()
s.close()