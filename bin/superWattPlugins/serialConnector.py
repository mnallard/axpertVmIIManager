import requests
import re
import os
import datetime
import crcmod
import serial
from binascii import unhexlify
from struct import pack
from crc16 import crc16xmodem
from serial import Serial

from abc import ABCMeta, abstractmethod
from utils.functions import Functions

from superWattPlugins.abstractClassSuperWattConnector import AbstractClassSuperWattConnector

class SerialConnector(AbstractClassSuperWattConnector):
   name="SerialConnector"
   def __init__(self):
      self.parameterSet=False;

   def defineIfParam(self,params):
      error=0
      if not isinstance(params,dict):
         Functions.log("ERR","Error on interface parameters. Wrong format for configuration" , "Serial.Connector")
         return 0

      if "port" in params:
         self.port=params['port']
      else:
         Functions.log("ERR","Error on interface parameters.Missing port","Serial.Connector")
         error+=1

      if "baudrate" in params:
         self.baudrate=params['baudrate']
      else:
         Functions.log("ERR","Error on interface parameters.Missing baudrate","Serial.Connector")
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
         Functions.log("ERR","Error on interface parameters.Missing bytesize","Serial.Connector")
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
         Functions.log("ERR","Error on interface parameters.Missing parity","Serial.Connector")
         error+=1

      if "stopbits" in params:
         self.stopbits=serial.STOPBITS_ONE
         if re.search("STOPBITS_ONE_POINT_FIVE",params['stopbits'],re.I):
            self.stopbits=serial.STOPBITS_ONE_POINT_FIVE
         if re.search("STOPBITS_TWO",params['stopbits'],re.I):
            self.stopbits=serial.STOPBITS_TWO        
      else:
         Functions.log("ERR","Error on interface parameters.Missing stopbits","Serial.Connector")
         error+=1

      if "timeout" in params:
         self.timeout=params['timeout']
      else:
         Functions.log("ERR","Error on interface parameters.Missing timeout","Serial.Connector")
         error+=1

      if "xonxoff" in params:
         self.xonxoff=False
         if re.search("true",params['xonxoff'],re.I):
            self.xonxoff=True
      else:
         Functions.log("ERR","Error on interface parameters.Missing xonxoff","Serial.Connector")
         error+=1

      if "rtscts" in params:
         self.rtscts=False;
         if re.search("true",params['rtscts'],re.I):
            self.rtscts=True
      else:
         Functions.log("ERR","Error on interface parameters.Missing rtscts","Serial.Connector")
         error+=1

      if "dsrdtr" in params:
         self.dsrdtr=False
         if re.search("true",params['dsrdtr'],re.I):
             self.dsrdtr=True 
      else:
         Functions.log("ERR","Error on interface parameters.Missing dsrdtr","Serial.Connector")
         error+=1

      if "writeTimeout" in params:
         self.writeTimeout=params['writeTimeout']
      else:
         Functions.log("ERR","Error on interface parameters.Missing writeTimeout","Serial.Connector")
         error+=1
      if(error):
         return 0
      self.parameterSet=True
      return 1

   def openConn(self):
      if not self.parameterSet:
         Functions.log("ERR","Error on interface parameters not successfully set" ,"Serial.Connector")
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
      try:
         self.serialConnect.open()
      except Exception as e:
         Functions.log("ERR","Error opening serial port: "+str(e),"Serial.Connector")
         return 0
      self.serialConnect.flushInput()
      self.serialConnect.flushOutput()
      return 1

   def closeConn(self):
      if not self.parameterSet:
         Functions.log("ERR","Error on interface parameters not successfully set" ,"Serial.Connector")
         return 0
      try:
         self.serialConnect.close()
      except Exception as e:
         Functions.log("ERR","Error closing serial port: "+str(e),"Serial.Connector")
         return 0
      return 1

   def sendSerialMesg(self,command):
      encoded_cmd = command.encode()
      checksum = crc16xmodem(encoded_cmd)
      request = encoded_cmd + pack('>H', checksum) + b'\r'
      ser=self.serialConnect
      ser.flushInput()
      ser.flushOutput()
      ser.write(request[:8])
      if len(request) > 8:
         ser.write(request[8:])
 
   def receiveSerialMesg(self):
      ser=self.serialConnect
      response = ser.read(100)
      response=response.decode("ISO-8859-1")
      #response=response.encode("ascii","ignore")
      return response
 
   def connTest(self):
      ser=self.serialConnect
      self.sendSerialMesg('QPIGS')
      mesg=self.receiveSerialMesg()
      return mesg 
 
