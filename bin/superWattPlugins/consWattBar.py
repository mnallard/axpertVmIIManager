import os
import re
import subprocess
import time
from superWattPlugins.abstractClassSuperWattMetrics import AbstractClassSuperWattMetrics 
from utils.functions import Functions

class M_consWattBar(AbstractClassSuperWattMetrics):
   name = "M_consWattBar"
      
   def runMetrics(self):
      Functions.log("INF", "Starting M_QPIGS", "M_QPIGS")
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
      Functions.log("INF", "Flushing data to influx", "M_Vmstat")
      self.flush("s")
      Functions.log("INF", "Ending  M_QPIGS", "M_QPIGS")
