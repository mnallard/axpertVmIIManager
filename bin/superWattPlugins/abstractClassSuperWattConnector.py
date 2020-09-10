import requests
import os
import datetime

from abc import ABCMeta, abstractmethod
from utils.functions import Functions


class AbstractClassSuperWattConnector():
   __metaclass__ = ABCMeta

   def __init__(self):
      self.error = 0
      self.errorText = "no_error"

   def defineInterfaceParameters(self,parameters):
      try:
         self.defineIfParam(parameters)
      except Exception as err:
         self.error = 1
         self.errorText = str(err).replace(" ", "_")
         Functions.log("ERR", "Error while running plugin : " +
                          str(err), "AbstractClassSuperWattConnector.defineIfParam") 

   def openConnection(self):
      try:
         self.openConn()
      except Exception as err:
         self.error = 1
         self.errorText = str(err).replace(" ", "_")
         Functions.log("ERR", "Error while running plugin : " +
                        str(err), "AbstractClassSuperWattConnector.openConnection")

   def closeConnection(self):
      try:
         self.closeConn()
      except Exception as err:
         self.error = 1
         self.errorText = str(err).replace(" ", "_")
         Functions.log("ERR", "Error while running plugin : " +
                        str(err), "AbstractClassSuperWattConnector.closeConnection")

   def testConnection(self):
      try:
         mesg=self.connTest()
      except Exception as err:
         self.error = 1
         self.errorText = str(err).replace(" ", "_")
         Functions.log("ERR", "Error while running plugin : " +
                        str(err), "AbstractClassSuperWattConnector.testConnection")
         return "Error on connection test"
      return mesg
