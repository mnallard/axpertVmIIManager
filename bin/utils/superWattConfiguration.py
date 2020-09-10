import os
import re
import subprocess
import time
import json
from utils.functions import Functions


class superWattConfiguration:
   name = "superWattConfiguration"

   def __init__(self, configurationFile):
      self.configurationFile = configurationFile
      self.confLoaded = 0
      self.sampling = {}
      self.maxRun = {}
      self.maxThreads = 10
      self.maxFork = 0
      self.daemonServiceCommands = []

   def loadConfiguration(self):
      if not os.path.isfile(self.configurationFile):
         Functions.log("ERR", self.configurationFile +  " does not exists !", "CORE")
         return 0

      try:
         jsonFile = open(self.configurationFile)
      except Exception as err:
         Functions.log("ERR", "Error loading configuration file", "CORE")
         Functions.log("ERR", str(err), "CORE")
         return 0
      with jsonFile as json_data:
         try:
            self.data_dict = json.load(json_data)
         except Exception as err:
            Functions.log(
                    "ERR", "Error parsing configuration file", "CORE")
            Functions.log("ERR", str(err), "CORE")
            jsonFile.close()
            return 0
      jsonFile.close()
      self.confLoaded = 1

   def retreiveSampling(self):
      if not self.confLoaded:
         Functions.log("ERR", "Error configuration file not opened", "CORE")
         return 0
      if "superWattMetrics" in self.data_dict:
         arr = self.data_dict['superWattMetrics']
         if isinstance(arr, list):
            self.conf = arr
            for item in self.conf:
               if isinstance(item, dict):
                  for confKey in item:
                     hashVal = item[confKey]
                     if isinstance(hashVal, dict):
                        for val in hashVal:
                           if val == "sampling":
                              self.sampling[confKey] = hashVal[val]
                           if val == "maxRun":
                              self.maxRun[confKey] = hashVal[val]
                     else:
                        Functions.log(
                                  "ERR", "Error in configuration file format", "CORE")
                        return 0
               else:
                  Functions.log(
                           "ERR", "Error in configuration file format", "CORE")
                  return 0
         else:
            Functions.log(
                   "ERR", "Error in configuration file format", "CORE")
            return 0
         return 1
      Functions.log("ERR", "Error with configuration file content", "CORE")
      return 0

   def retreiveSchedulerConf(self):
      if not self.confLoaded:
         Functions.log("ERR", "Error configuration file not opened", "CORE")
         return 0
      if "shedulerConfig" in self.data_dict:
         arr = self.data_dict['shedulerConfig']
         if isinstance(arr, dict):
            for confKey in arr:
               if confKey == "maxThreads":
                  self.maxThreads = arr[confKey]
               if confKey == "maxFork":
                  self.maxFork = arr[confKey]
         else:
            Functions.log(
                 "ERR", "Error in configuration file format", "CORE")
            return 0
      else:
         Functions.log("ERR", "Error in configuration file format", "CORE")
         return 0
      return 1

   def retreiveInfluxDbConf(self):
      if not self.confLoaded:
         Functions.log("ERR", "Error configuration file not opened", "CORE")
         return 0
      if "influxDbConfig" in self.data_dict:
         arr = self.data_dict['influxDbConfig']
         if isinstance(arr, dict):
            for confKey in arr:
               if confKey == "influxDbUrl":
                  self.influxDbUrl = arr[confKey]
               if confKey == "influxDbPort":
                  self.influxDbPort = arr[confKey]
               if confKey == "influxDbName":
                  self.influxDbName = arr[confKey]
         else:
            Functions.log(
                    "ERR", "Error in configuration file format", "CORE")
            return 0
      else:
         Functions.log("ERR", "Error in configuration file format", "CORE")
         return 0
      return 1

   def retreiveSerialConProp(self):
      if not self.confLoaded:
         Functions.log("ERR", "Error configuration file not opened", "CORE")
         return 0
      if "superWattSerialConnectionParameters" in self.data_dict:
         arr = self.data_dict['superWattSerialConnectionParameters']
         if isinstance(arr, dict):
            self.serialConProp=arr
            return 1
         else:
            Functions.log(
                   "ERR", "Error in configuration file format", "CORE")
            return 0
      else:
         Functions.log("ERR", "Error in configuration file format", "CORE")
         return 0
      return 1

   def retreiveSerialConProp4pylontech(self):
      if not self.confLoaded:
         Functions.log("ERR", "Error configuration file not opened", "CORE")
         return 0
      if "superWattSerialConnectionParameters4pylontech" in self.data_dict:
         arr = self.data_dict['superWattSerialConnectionParameters4pylontech']
         if isinstance(arr, dict):
            self.serialConProp4pylontech=arr
            return 1
         else:
            Functions.log(
                   "ERR", "Error in configuration file format", "CORE")
            return 0
      else:
         Functions.log("ERR", "Error in configuration file format", "CORE")
         return 0
      return 1

   def retreiveDaemonServiceConfig(self):
      if not self.confLoaded:
         Functions.log("ERR", "Error configuration file not opened", "CORE")
         return 0
      if "daemonServiceConfig" in self.data_dict:
         arr = self.data_dict['daemonServiceConfig']
         if isinstance(arr, dict):
            for confKey in arr:
               if confKey == "port":
                  self.daemonPort = arr[confKey]
               if confKey == "maxCon":
                  self.daemonMaxCon = arr[confKey]
         else:
            Functions.log(
                    "ERR", "Error in configuration file format", "CORE")
            return 0
      else:
         Functions.log("ERR", "Error in configuration file format", "CORE")
         return 0
      return 1

   def retreiveSuperWattGeneralConfig(self):
      if not self.confLoaded:
         Functions.log("ERR", "Error configuration file not opened", "CORE")
         return 0
      if "superWattGeneralConfig" in self.data_dict:
         arr = self.data_dict['superWattGeneralConfig']
         if isinstance(arr, dict):
            for confKey in arr:
               if confKey == "superWattPlugInPath":
                  self.superWattPlugInPath = arr[confKey]
         else:
            Functions.log(
                 "ERR", "Error in configuration file format", "CORE")
            return 0
      else:
         Functions.log("ERR", "Error in configuration file format", "CORE")
         return 0
      return 1

   def retreiveDaemonServiceCommands(self):
      if not self.confLoaded:
         Functions.log("ERR", "Error configuration file not opened", "CORE")
         return 0
      if "daemonServiceCommands" in self.data_dict:
         arr = self.data_dict['daemonServiceCommands']
         if isinstance(arr, dict):
            for confKey in arr:
               self.daemonServiceCommands.append(confKey)
         else:
            Functions.log(
                    "ERR", "Error in configuration file format", "CORE")
            return 0
      else:
         Functions.log("ERR", "Error in configuration file format", "CORE")
         return 0
      return 1

   def getSamplingFor(self, metrixName):
      if not isinstance(self.sampling, dict):
         Functions.log(
                "ERR", "Error configuration not loaded in object metrixConfiguration", "CORE")
         return 0
      if metrixName in self.sampling:
         return self.sampling[metrixName]
      if "Default" in self.sampling:
         return self.sampling['Default']

   def getMaxRunFor(self, metrixName):
      if not isinstance(self.maxRun, dict):
         Functions.log(
                "ERR", "Error configuration not loaded in object metrixConfiguration", "CORE")
         return 0
      if metrixName in self.maxRun:
         return self.maxRun[metrixName]
      if "Default" in self.maxRun:
         return self.maxRun['Default']

   def checkConfiguration(self):
      if not self.retreiveSampling():
         Functions.log(
             "DEAD", "Error getting data from conf file about metric sampling", "CORE")
      if not self.retreiveSchedulerConf():
         Functions.log(
              "DEAD", "Error getting data from conf file about scheduler config", "CORE")
      if not self.retreiveDaemonServiceCommands():
         Functions.log(
              "DEAD", "Error getting data from conf file about services commands", "CORE")
      if not self.retreiveInfluxDbConf():
         Functions.log(
              "DEAD", "Error getting data from conf file about influxDB conf", "CORE")
      if not self.retreiveDaemonServiceConfig():
         Functions.log(
              "DEAD", "Error getting data from conf file about influxDB conf", "CORE")
      if not self.retreiveSuperWattGeneralConfig():
         Functions.log(
              "DEAD", "Error getting data from conf file about Metrix general config", "CORE")
      if not self.retreiveSerialConProp():
         Functions.log(
              "DEAD", "Error getting data from conf file about Metrix serial connection config", "CORE") 
      if not self.retreiveSerialConProp4pylontech():
          Functions.log(
              "DEAD", "Error getting data from conf file about Metrix serial connection config for pylontech", "CORE")
      return 1

   def getMaxThreadForScheduler(self):
      return self.maxThreads

   def getMaxForkForScheduler(self):
      return self.maxFork

   def getServicesCommandList(self):
      return self.daemonServiceCommands

   def getDaemonServicePort(self):
      return self.daemonPort

   def getDaemonMaxCon(self):
      return self.daemonMaxCon

   def getInfluxDbUrl(self):
      return self.influxDbUrl

   def getInfluxDbPort(self):
      return self.influxDbPort

   def getInfluxDbName(self):
      return self.influxDbName

   def getMetrixPlugInPath(self):
      return self.superWattPlugInPath

   def getSerialConProp(self):
      return self.serialConProp
   
   def getSerialConProp4pylontech(self):
      return self.serialConProp4pylontech
