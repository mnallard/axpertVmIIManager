import os
import re
import subprocess
import time
from superWattPlugins.abstractClassSuperWattMetrics import AbstractClassSuperWattMetrics 
from utils.functions import Functions

class M_pylontech(AbstractClassSuperWattMetrics):
   name = "M_pylontech"
   def _getValueFromPylontech(self):
      self.values=[[],[]]
      serialConnection=self.serialCon
      serialConnection.openConn()
      serialConnection.sendSerialMesg('pwr 1')
      self.values[0]=serialConnection.receiveSerialMesg()
      serialConnection.sendSerialMesg('pwr 2')
      self.values[1]=serialConnection.receiveSerialMesg()
      serialConnection.closeConn()
      tabParams4Pwr=['Voltage','Current','Temperature','Coulomb']
      indicators=dict()
      for i in range(0,2):
         for line in self.values[i]:
            for itemToGrab in tabParams4Pwr:
               if re.search("^\s+"+itemToGrab+"\s*:",line):
                  result=re.split(":",line)
                  value=re.match('\s*\S+',result[1]).group()
                  value=value.replace(" ","")
                  if itemToGrab=="Voltage" or itemToGrab=="Current" or itemToGrab=="Temperature":
                     value=int(value)/1000
                  itemToGrab=itemToGrab.replace(" ","")
                  itemToGrab=itemToGrab.replace(".","")
                  indicators[itemToGrab+str(i+1)]=value
      indicators['packVoltage']=(float(indicators['Voltage1'])+float(indicators['Voltage2']))/2 
      indicators['packCurrent']=(float(indicators['Current1'])+float(indicators['Current2']))
      indicators['packCapacity']=(float(indicators['Coulomb1'])+float(indicators['Coulomb2']))/2
      return indicators

   def runMetrics(self):
      Functions.log("INF", "STARTING M_pylontech", "M_pylontech")
      valuesDict=self._getValueFromPylontech()
      #print(valuesDict)
      firstField=True
      payload="pylontech_pwr"
      for fields in valuesDict.keys():
         if firstField:
            payload+=" "+fields+"="+str(valuesDict[fields])
            firstField=False
         else:
            payload+=","+fields+"="+str(valuesDict[fields])
      self.putMetrics(payload)
      #Functions.log("INF", "Flushing data to influx", "M_pylontech")
      self.flush("s")
      Functions.log("INF", "ENDING  M_pylontech", "M_pylontech")
