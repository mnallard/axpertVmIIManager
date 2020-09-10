import requests
import re
import os
import datetime
import crcmod
import serial
import time
from binascii import unhexlify
from struct import pack
from crc16 import crc16xmodem
from serial import Serial

from abc import ABCMeta, abstractmethod
from utils.functions import Functions

from superWattPlugins.abstractClassSuperWattConnector import AbstractClassSuperWattConnector

class SerialConnector4pylontech(AbstractClassSuperWattConnector):
   name="SerialConnector4pylontech"
   def __init__(self):
      self.parameterSet=False;

   def defineIfParam(self,params):
      error=0
      if not isinstance(params,dict):
         Functions.log("ERR","Error on interface parameters. Wrong format for configuration" , "Serial.Connector4pylontech")
         return 0

      if "port" in params:
         self.port=params['port']
      else:
         Functions.log("ERR","Error on interface parameters.Missing port","Serial.Connector4pylontech")
         error+=1

      if "baudrate" in params:
         self.baudrate=params['baudrate']
      else:
         Functions.log("ERR","Error on interface parameters.Missing baudrate","Serial.Connector4pylontech")
         error+=1 
 
      if "bytesize" in params:
         self.bytesize=serial.EIGHTBITS
         if re.search("SEVENBITS",params['bytesize'],re.I):
            self.bytesize=serial.SEVENBITS
         if re.search("SIXBITS",params['bytesize'],re.I):
            self.bytesize=serial.SIXBITS
         if re.search("FIVEBITS",params['bytesize'],re.I):
            self.bytesize=serial.FIVEBITS
      else:
         Functions.log("ERR","Error on interface parameters.Missing bytesize","Serial.Connector4pylontech")
         error+=1   

      if "parity" in params:
         self.parity=serial.PARITY_NONE
         if re.search("PARITY_EVEN",params['parity'],re.I): 
            self.parity=serial.PARITY_EVEN
         if re.search("PARITY_ODD",params['parity'],re.I):
            self.parity=serial.PARITY_ODD
         if re.search("PARITY_SPACE",params['parity'],re.I):
            self.parity=serial.PARITY_SPACE 
         if re.search("PARITY_MARK",params['parity'],re.I):
            self.parity=serial.PARITY_MARK

      else:
         Functions.log("ERR","Error on interface parameters.Missing parity","Serial.Connector4pylontech")
         error+=1

      if "stopbits" in params:
         self.stopbits=serial.STOPBITS_ONE
         if re.search("STOPBITS_ONE_POINT_FIVE",params['stopbits'],re.I):
            self.stopbits=serial.STOPBITS_ONE_POINT_FIVE
         if re.search("STOPBITS_TWO",params['stopbits'],re.I):
            self.stopbits=serial.STOPBITS_TWO        
      else:
         Functions.log("ERR","Error on interface parameters.Missing stopbits","Serial.Connector4pylontech")
         error+=1

      if "timeout" in params:
         self.timeout=params['timeout']
      else:
         Functions.log("ERR","Error on interface parameters.Missing timeout","Serial.Connector4pylontech")
         error+=1

      if "xonxoff" in params:
         self.xonxoff=False
         if re.search("true",params['xonxoff'],re.I):
            self.xonxoff=True
      else:
         Functions.log("ERR","Error on interface parameters.Missing xonxoff","Serial.Connector4pylontech")
         error+=1

      if "rtscts" in params:
         self.rtscts=False;
         if re.search("true",params['rtscts'],re.I):
            self.rtscts=True
      else:
         Functions.log("ERR","Error on interface parameters.Missing rtscts","Serial.Connector4pylontech")
         error+=1

      if "dsrdtr" in params:
         self.dsrdtr=False
         if re.search("true",params['dsrdtr'],re.I):
             self.dsrdtr=True 
      else:
         Functions.log("ERR","Error on interface parameters.Missing dsrdtr","Serial.Connector4pylontech")
         error+=1

      if "writeTimeout" in params:
         self.writeTimeout=params['writeTimeout']
      else:
         Functions.log("ERR","Error on interface parameters.Missing writeTimeout","Serial.Connector4pylontech")
         error+=1
      if(error):
         return 0
      self.parameterSet=True
      return 1

   def openConn(self):
      if not self.parameterSet:
         Functions.log("ERR","Error on interface parameters not successfully set" ,"Serial.Connector4pylontech")
         return 0
      self.serialConnect=serial.Serial()
      self.serialConnect.port=self.port
      self.serialConnect.baudrate=self.baudrate
      self.serialConnect.bytesize=self.bytesize
      self.serialConnect.parity=self.parity
      self.serialConnect.stopbits=self.stopbits  
      self.serialConnect.timeout=self.timeout
      self.serialConnect.xonxoff=self.xonxoff
      self.serialConnect.rtscts=self.rtscts
      self.serialConnect.dsrdtr=self.dsrdtr
      self.serialConnect.writeTimeout=self.writeTimeout
      connectedErr=1
      while connectedErr:
         try:
            self.serialConnect.open()
            connectedErr=0
         except Exception as e:
            Functions.log("ERR","Error opening serial port: "+str(e),"Serial.Connector4pylontech")
            time.sleep(1)
            connectedErr+=1
         if (connectedErr>3):
            return 0
      self.serialConnect.flushInput()
      self.serialConnect.flushOutput()
      msg=bytearray([0x0D,0x0A])
      self.serialConnect.write(msg)
      while True:
         response=self.serialConnect.readline()
         if not response:
            break
      return 1

   def closeConn(self):
      if not self.parameterSet:
         Functions.log("ERR","Error on interface parameters not successfully set" ,"Serial.Connector4pylontech")
         return 0
      try:
         self.serialConnect.close()
      except Exception as e:
         Functions.log("ERR","Error closing serial port: "+str(e),"Serial.Connector4pylontech")
         return 0
      return 1

   def sendSerialMesg(self,command):
      ser=self.serialConnect
      ser.flushInput()
      ser.flushOutput()
      encoded_cmd=command
      cmd=command.encode()
      sequence=bytearray(cmd)
      sequence.append(0x0d)
      try:
         ser.write(sequence)
      except Exception as e:
         print(e)
         return 0
      return 1
 
   def receiveSerialMesg(self):
      ser=self.serialConnect
      msgBuff=[]
      while True:
         response=ser.readline()
         if not response:
            break
         response=response.decode("ascii")
         msgBuff.append(str(response))
      return msgBuff
 
   def connTest(self):
      ser=self.serialConnect
      self.sendSerialMesg('pwr') 
      buff=self.receiveSerialMesg()
      resultString=""
      for line in buff:
         resultString+=line
      return resultString 
 
