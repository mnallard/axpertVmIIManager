#! /usr/bin/python

import serial ,time, sys, string
import os
import re
from serial import Serial
import binascii

ser=serial.Serial()
ser.port="/dev/ttyUSB1"
ser.baudrate = 1200
ser.bytesize = serial.EIGHTBITS     #number of bits per bytes
ser.parity = serial.PARITY_NONE     #set parity check: no parity
ser.stopbits = serial.STOPBITS_ONE  #number of stop bits
ser.timeout = 1               #block read
#ser.timeout = 1                     #non-block read
ser.xonxoff = False                 #disable software flow control
ser.rtscts = False                  #disable hardware (RTS/CTS) flow control
ser.dsrdtr = False                  #disable hardware (DSR/DTR) flow control

try:
    ser.close()
except Exception as e:
    print ("Error closing serial port: " + str(e))



ser.open()

initSequence=bytearray([0x7E,0x32,0x30,0x30,0x31,0x34,0x36,0x38,0x32,0x43,0x30,0x30,0x34,0x38,0x35,0x32,0x30,0x46,0x43,0x43,0x33,0x0D])
ser.write(initSequence)
ser.close()

command=sys.argv[1:][0]
encoded_cmd=command
cmd=command.encode()
sequence=bytearray(cmd)
ser.baudrate = 115200
try:
    ser.open()
except Exception as e:
    print ("Error opening serial port: " + str(e))
    exit()
if not ser.is_open:
   print ("Error serial port not opened")
   exit()

msg=bytearray([0x0d,0x0a])
ser.write(msg)
ser.flushInput()
ser.flushOutput()
while True:
   response=ser.readline()
   if not response:
      break
   response=response.decode('ascii')
   response=str(response)
   print(response)

try:
   sequence.append(0x0d)
   ser.write(sequence)
   print ("Write "+str(sequence))
   while True:
      response=ser.readline()
      if not response:
         break
      response=response.decode('ascii')
      response=str(response)
      print(response)

except Exception as e:
   print(e);
   exit()
ser.close()
