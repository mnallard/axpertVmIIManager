#! /usr/bin/python

import serial ,time, sys, string
import os
import re
from serial import Serial
import binascii

ser=serial.Serial()
ser.port="/dev/ttyUSB1"
ser.bytesize = serial.EIGHTBITS     #number of bits per bytes
ser.parity = serial.PARITY_NONE     #set parity check: no parity
ser.stopbits = serial.STOPBITS_ONE  #number of stop bits
ser.timeout = 1               #block read
#ser.timeout = 1                     #non-block read
ser.xonxoff = False                 #disable software flow control
ser.rtscts = False                  #disable hardware (RTS/CTS) flow control
ser.dsrdtr = False                  #disable hardware (DSR/DTR) flow control
ser.baudrate=115200

try:
    ser.open()
except Exception as e:
    print ("Error opening serial port: " + str(e))
    exit()
if not ser.is_open:
   print ("Error serial port not opened")
   exit()

msg=bytearray([0x0D,0x0A])
ser.write(msg)
ser.readline()


def closeConn(s):
   try:
      s.serialConnect.close()
   except Exception as e:
      return 0
   return 1

def sendSerialMesg(s,command):
   s.flushInput()
   s.flushOutput()
   encoded_cmd=command
   cmd=command.encode()
   sequence=bytearray(cmd)
   sequence.append(0x0d)
   try:
      s.write(sequence)
   except Exception as e:
      print(e)
      return 0
   return 1

def receiveSerialMesg(s):
   msgBuff=[]
   while True:
      response=s.readline()
      if not response:
         break
      response=response.decode("ascii")
      msgBuff.append(str(response))
   return msgBuff


values=[[],[],[],[]]
sendSerialMesg(ser,'pwr 1')
values[0]=receiveSerialMesg(ser)
sendSerialMesg(ser,'pwr 2')
values[1]=receiveSerialMesg(ser)
sendSerialMesg(ser,'bat 1')
values[2]=receiveSerialMesg(ser)
sendSerialMesg(ser,'bat 2 ')
values[3]=receiveSerialMesg(ser)
ser.close()
tabParams4Pwr=['Voltage','Current','Temperature','Coulomb','Basic Status','Charge Sec.']
indicators=dict()
for i in range(0,2):
   for line in values[i]:
      if i<2:
         for itemToGrab in tabParams4Pwr:
            if re.search("^\s+"+itemToGrab+"\s*:",line):
               result=re.split(":",line)
               value=re.match('\s*\S+',result[1]).group()
               value=value.replace(" ","")
               if itemToGrab=="Voltage" or itemToGrab=="Current" or itemToGrab=="Temperature":
                  value=int(value)/1000
                  indicators[itemToGrab+str(i+1)]=str(value)

print(indicators)
ser.close()
