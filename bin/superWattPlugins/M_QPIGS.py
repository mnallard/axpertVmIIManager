import os
import re
import subprocess
import time
from superWattPlugins.abstractClassSuperWattMetrics import AbstractClassSuperWattMetrics 
from utils.functions import Functions

class M_QPIGS(AbstractClassSuperWattMetrics):
   name = "M_QPIGS"
   def _getValueFromInverter(self):
      self.QPIGSfields=['GridVoltage','GridFrequency','OutputVoltage','OutputFrequency','OutputApparentPower','OutputActivePower','OutputLoadPercent','BusVoltage','BatteryVoltage','BatteryChargingCurrent','BatteryCapacity','InverterHeatSinkTemperature','PVInputCurrent','PVInputVoltage','BatteryVoltageFromSCC','BatteryDischargeCurrent','DeviceStatus']
      serialConnection=self.serialCon
      serialConnection.openConn()
      serialConnection.sendSerialMesg('QPIGS')
      mesg=serialConnection.receiveSerialMesg()
      serialConnection.closeConn()
      if re.search("nak",mesg,re.I):
         Functions.log("ERR", "M_QPIGS : Error un serial communication. Getting nak", "M_QPIGS")
         return "Error"
      tabLine = re.split('\s+',mesg)
      jsonDict={}
      for fields in self.QPIGSfields:
         val=tabLine.pop(0)
         if re.match("^\(",val):
            val=val[1:]
         jsonDict[fields]=val
      PVInputActivePower=float(jsonDict['PVInputVoltage'])*float(jsonDict['PVInputCurrent'])
      BuyedPower=float(jsonDict['OutputActivePower'])-PVInputActivePower
      pylontechPower=float(jsonDict['BatteryVoltage'])*float(jsonDict['BatteryDischargeCurrent'])
      BuyedPower=BuyedPower-pylontechPower
      if BuyedPower<0.0:
         BuyedPower=0
      jsonDict['PVInputActivePower']=str(PVInputActivePower)
      jsonDict['BuyedPower']=str(BuyedPower)
      jsonDict['pylonTechPower']=str(pylontechPower)
      return jsonDict
      
   def runMetrics(self):
      Functions.log("INF", "STARTING M_QPIGS", "M_QPIGS")
      valuesDict=self._getValueFromInverter()
      firstField=True 
      payload="superWatt_QPIGS"
      for fields in valuesDict.keys():  
         if firstField:
            payload+=" "+fields+"="+valuesDict[fields]
            firstField=False
         else:
            payload+=","+fields+"="+str(valuesDict[fields])
      self.putMetrics(payload)
      #Functions.log("INF", "Flushing data to influx", "M_QPIGS")
      self.flush("s")
      Functions.log("INF", "ENDING  M_QPIGS", "M_QPIGS")
