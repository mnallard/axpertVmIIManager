import requests
import os
import datetime

from abc import ABCMeta, abstractmethod
from utils.functions import Functions

from superWattPlugins.abstractClassSuperWattConnector import AbstractClassSuperWattConnector
from superWattPlugins.serialConnector import SerialConnector


class AbstractClassSuperWattMetrics():
   __metaclass__ = ABCMeta

   def __init__(self, influxDbUrl, influxDbPort, influxDbName, serialCon):
      self.influxDbUrl=influxDbUrl
      self.influxDbPort=influxDbPort
      self.influxDbName=influxDbName
      self.error=0
      self.starttime=int(datetime.datetime.now().strftime("%s")) * 1000
      self.errorText="no_error"
      self.payload=""
      self.lastPayload=""
      self.metricsLines=[]
      self.serialCon=serialCon

   def run(self):
      try:
         self.runMetrics()
      except Exception as err:
         self.error = 1
         self.errorText = str(err).replace(" ", "_")
         Functions.log("ERR", "Error while running plugin : " +
                             str(err), "AbstractClassSuperWattMetrics.runMetrics")

   def putMetrics(self, metricsLine):
      #Functions.log("DBG", "Storing metricsLine:" + metricsLine, "AbstractClassSuperWattMetrics.putMetrix")
      self.metricsLines.append(metricsLine)

   def flush(self, precision):
      Functions.log("DBG", "Flushing data to influxdb",
                      "AbstractClassSuperWattMetrics.flush")
      METRIX_URL=str(self.influxDbUrl)+":"+str(self.influxDbPort)
      METRIX_DB=self.influxDbName
      targeturl=METRIX_URL+'/write?db='+METRIX_DB+'&precision='+precision
      self.payload = ""
      for line in self.metricsLines:
         self.payload+=str(line)+"\n"
      self.metricsLines = []
      headers={'Content-Type':'application/octet-stream'}
      Functions.log("DBG", "Sending" + targeturl +
                   self.payload, "AbstractClassSuperWattMetrics.flush")
      r=requests.post(targeturl,data=self.payload,headers=headers)
      Functions.log("INF","Sending to INFLUXB :" + self.payload,"CORE")
      self.lastPayload=targeturl+self.payload
      Functions.log("DBG", "Request status " +
                   str(r.status_code), "AbstractClassSuperWattMetrics.flush")

   def getLastPayloadSent(self):
      Functions.log("DBG", "Last payload : "+self.lastPayload, "CORE")
      return self.lastPayload
