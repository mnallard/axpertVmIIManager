import os
import re
import subprocess
import time
import json
import socket
import select

from utils.functions import Functions


class superWattNetworkServices:
    name = "superWattNetworkServices"

    def __init__(self, port, nbMaxCon):
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverSocket.setblocking(0)
        Functions.log("INF", "Binding server socket to " +
                      str(socket.gethostname())+":"+str(port), "CORE")
        serverSocket.bind((socket.gethostname(), port))
        serverSocket.listen(nbMaxCon)
        Functions.log(
            "INF", "Setting daemon service max connections to "+str(nbMaxCon), "CORE")
        self.serverSocket = serverSocket
        self.inputs = [self.serverSocket]
        self.outputs = []
        self.mesgList = []
        self.nbConnOpened = 0

    def manageNetworkService(self):
        readable, writable, exceptional = select.select(
            self.inputs, self.outputs, self.inputs, 0.1)
        for sock in readable:
            if sock is self.serverSocket:
                newConnection, clientAddress = self.serverSocket.accept()
                newConnection.setblocking(0)
                Functions.log(
                    "INF", "New connection on socket from "+str(clientAddress), "CORE")
                self.inputs.append(newConnection)
                self.nbConnOpened += 1
            else:
                try:
                    serviceData = sock.recv(1024)
                except Exception as err:
                    Functions.log("ERR", "Error while reading socket.", "CORE")
                    Functions.log("ERR", str(err), "CORE")
                    break

                if serviceData:
                    Functions.log("INF", "Received message :" +
                                  serviceData.decode()+":", "CORE")
                    messageArray = [sock, serviceData.decode()]
                    self.mesgList.append(messageArray)
                else:
                    self.inputs.remove(sock)
                    self.nbConnOpened -= 1
                    sock.close()

        for sock in exceptional:
            self.input.remove(sock)
            self.nbConnOpened -= 1
            sock.close()

        if len(self.mesgList) > 100:
            Functions.log(
                "ERR", "Internal message queue exceed 100 messages. Clearing queue", "CORE")
            for sock in self.inputs:
                if sock is self.serverSocket:
                    pass
                else:
                    self.inputs.remove(sock)
                    self.nbConnOpened -= 1
                    sock.close()
                    Functions.log(
                        "ERR", "Closing tcp connection for cleaning", "CORE")
            self.mesgList = []

    def getServicesMessages(self):
        if len(self.mesgList):
            mesgArray = self.mesgList[0]
            del(self.mesgList[0])
        else:
            mesgArray = []
        return mesgArray

    def outPutMessageQueueForDebug(self):
        for arr in self.mesgList:
            Functions.log("INF", str(arr), "CORE")

    def nbConnOpened(self):
        return self.nbConnOpened

    def badServiceAnswer(self, sock):
        try:
            sock.send("Bad query for services commands. Stopping now\n".encode())
        except Exception as err:
            Functions.log("ERR", "unable to write on socket.", "CORE")
            Functions.log("ERR", str(err), "CORE")
        if sock in self.inputs:
            self.inputs.remove(sock)
        Functions.log("INF", "Closing connection for " +
                      str(sock.getpeername()), "CORE")
        try:
            sock.close()
        except Exception as err:
            Functions.log("ERR", "Error while closing socket.", "CORE")
            Functions.log("ERR", str(err), "CORE")

    def goodServiceAnswer(self, sock, message):
        try:
            sock.send(message.encode())
        except Exception as err:
            Functions.log("ERR", "unable to write on socket.", "CORE")
            Functions.log("ERR", str(err), "CORE")
        if sock in self.inputs:
            self.inputs.remove(sock)
        Functions.log("INF", "Closing connection for " +
                      str(sock.getpeername()), "CORE")
        try:
            sock.close()
        except Exception as err:
            Functions.log("ERR", "Error while closing socket.", "CORE")
            Functions.log("ERR", str(err), "CORE")

    def decodeNetworkMessage(self, message, autorizedCommands):
        operation = ""
        op = ""
        data = ""
        try:
            serviceReq = json.loads(message)
        except Exception as err:
            Functions.log("ERR", "unable to decode json request", "CORE")
            Functions.log("ERR", str(err), "CORE")
            return 0
        if isinstance(serviceReq, dict):
            if ("superWattServiceRequest" in serviceReq):
                payload = serviceReq["superWattServiceRequest"]
                if isinstance(payload, dict):
                    if ("operation" in payload):
                        operation = payload["operation"]
                    else:
                        Functions.log(
                            "ERR", "Service command not well formated", "CORE")
                        return 0
                else:
                    Functions.log(
                        "ERR", "Service command not well formated", "CORE")
                if ("data" in payload):
                    operation += ":"+str(payload["data"])
            else:
                Functions.log(
                    "ERR", "Service command not well formated", "CORE")
                return 0
        else:
            Functions.log("ERR", "Service command not well formated", "CORE")
            return 0
        try:
            (op, data) = operation.split(":")
        except Exception as err:
            op = operation
            data = ""
        if op in autorizedCommands:
            Functions.log("INF", "Service command :" +
                          str(op)+": authorized", "CORE")
            return str(operation)
        else:
            Functions.log("ERR", "Service command " +
                          str(op)+" unknown", "CORE")
            return 0
