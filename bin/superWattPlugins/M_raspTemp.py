import os
import re
import subprocess
import time
from superWattPlugins.abstractClassSuperWattMetrics import AbstractClassSuperWattMetrics 
from utils.functions import Functions

class M_raspTemp(AbstractClassSuperWattMetrics):
   name = "M_raspTemp"
      
   def runMetrics(self):
      Functions.log("INF", "STARTING M_raspTemp", "M_raspTemp")
      payload="pi4measurements"
      temp=os.popen("vcgencmd measure_temp").readline()
      temp=temp.replace("temp=","")
      shortTemp=re.match("^\d+\.\d+",temp)
      if shortTemp:
         payload+=" temp="+str(shortTemp[0])
         self.putMetrics(payload)
         #Functions.log("INF", "Flushing data to influx", "M_raspTemp")
         self.flush("s")
      Functions.log("INF", "ENDING M_raspTemp", "M_raspTemp")
