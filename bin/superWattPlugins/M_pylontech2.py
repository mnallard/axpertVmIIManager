import os
import re
import subprocess
import time
from superWattPlugins.abstractClassSuperWattMetrics import AbstractClassSuperWattMetrics 
from utils.functions import Functions

class M_pylontech2(AbstractClassSuperWattMetrics):
   name = "M_pylontech2"
   def _getValueFromPylontech(self):
      self.values=[[],[]]
      serialConnection=self.serialCon
      serialConnection.openConn()
      serialConnection.sendSerialMesg('bat 1')
      self.values[0]=serialConnection.receiveSerialMesg()
      serialConnection.sendSerialMesg('bat 2 ')
      self.values[1]=serialConnection.receiveSerialMesg()
      serialConnection.closeConn()
      tabParams4Bat=['Battery','Volt','Curr','Tempr','BaseState','VoltState','CurrentState','TempState','Coulomb']
      indicators=dict()
      batnum=1
      for i in range(0,2):
         if i:
            batnum=2
         for line in self.values[i]:
            if re.search("^\d+",line):
               result=re.split("\s+",line)
               cellNumber=result[0] 
               for i in range(1,9):
                  value=result[i]
                  value=value.replace(" ","")
                  value=value.replace("%","")
                  if(i<4):
                     value=int(result[i])/1000
                     indicators['Bat'+str(batnum)+"Cell"+str(cellNumber)+tabParams4Bat[i]]=value 
      return indicators

   def runMetrics(self):
      Functions.log("INF", "STARTING M_pylontech2", "M_pylontech2")
      valuesDict=self._getValueFromPylontech()
      #print(valuesDict)
      firstField=True
      payload="pylontech_bat"
      for fields in valuesDict.keys():
         if firstField:
            payload+=" "+fields+"="+str(valuesDict[fields])
            firstField=False
         else:
            payload+=","+fields+"="+str(valuesDict[fields])
      self.putMetrics(payload)
      #Functions.log("INF", "Flushing data to influx", "M_pylontech2")
      self.flush("s")
      Functions.log("INF", "ENDING  M_pylontech2", "M_pylontech2")
