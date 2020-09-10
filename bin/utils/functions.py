import datetime
import subprocess
import re
import sys
import threading
import os

class Functions:

    logLevel = {"ERR": 0,
                "INF": 1,
                "DBG": 2,
                "DEAD": 3
                }
    lLevel = 1
    fileLog=None
    logPath="/users/superWattMetrics/log"
    @staticmethod
    def log(level, message, source):
        if Functions.fileLog == None:
            if not os.path.exists(Functions.logPath):
                os.mkdir(Functions.logPath, mode = 0o777)
            Functions.fileLog = open(Functions.logPath+"/daemon.log", "a")
        date = str(datetime.datetime.now())
        message = date + " " + \
            "[" + threading.current_thread().name + "] " + level + \
            " " + source + " " + message
        Functions.fileLog.write(message + '\n')
        if (level in Functions.logLevel):
            levelValue = Functions.logLevel[level]
            if (levelValue <= Functions.lLevel):
                print(message)
            if (level == "DEAD"):
                print(message)
                sys.exit(1)

    @staticmethod
    def getFieldFromString(string, delimiter, fieldNumber):
        return re.split(delimiter, string)[fieldNumber]

    @staticmethod
    def setLogLevel(level):
        if (level in Functions.logLevel):
            Functions.lLevel = Functions.logLevel[level]
            return 1
        return 0

    @staticmethod
    def getFirstMatchInAFile(string, file):
        with open(file, "r") as f:
            for line in f.readlines():
                if string in line:
                    f.close()
                    return(line.rstrip('\n'))

    @staticmethod
    def getFirstMatchInArray(string, array):
        for line in array:
            if string in line:
                return(line.rstrip('\n'))

    @staticmethod
    def getLastMatchInArray(string, array):
        returnLine = ""
        for line in array:
            if string in line:
                returnLine = line
        return returnLine

    @staticmethod
    def getLastMatchReInArray(regexp, array):
        returnLine = ""
        for line in array:
            if re.match(regexp, line) is not None:
                returnLine = line
        return returnLine

    @staticmethod
    def getFirstMatchInLine(string, line):
        array = line.split("\n")
        return Functions.getFirstMatchInArray(string, array).rstrip('\n')

    @staticmethod
    def displayFromLastSeenPatternFromArray(string, array):
        returnArray = []
        for line in array:
            if string in line:
                del returnArray[:]
                returnArray.append(line)
            else:
                returnArray.append(line)
        return returnArray

    @staticmethod
    def getLastMatchInLine(string, line):
        array = line.split("\n")
        return Functions.getLastMatchInArray(string, array).rstrip('\n')

    @staticmethod
    def kommandShell(aKommand):
        return_output = subprocess.check_output(
            aKommand, shell=True).decode().rstrip('\n')
        return return_output

    @staticmethod 
    def sshKommand(target,command):
        SSHUX_CMD="/usr/bin/ssh -l sshux -n -o Batchmode=yes -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=QUIET -o ConnectTimeout=5 -i /psa/home/sshux/.ssh/id_dsa"
        return Functions.kommandShell( SSHUX_CMD + " " + target + " " + command)

    @staticmethod
    def scpRetrieveKommand(source,remoteFile,localFile):
        SCP_CMD="/usr/bin/scp -o Batchmode=yes -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=QUIET -o ConnectTimeout=5 -i /psa/home/sshux/.ssh/id_dsa"
        return Functions.kommandShell( SCP_CMD + " sshux@" + source +":" + remoteFile + " " + localFile)

    @staticmethod
    def kommandShellInArray(aKommand):
        return_output = Functions.kommandShell(aKommand).split('\n')
        return return_output

    @staticmethod
    def loadFileInALine(file):
        lines = ""
        with open(file, "r") as f:
            for line in f.readlines():
                lines += line + "\n"
            f.close()
        return(lines.rstrip('\n+'))

    @staticmethod
    def loadFileInArray(file):
        lines = []
        with open(file, "r") as f:
            for line in f.readlines():
                lines.append(line.rstrip('\n+'))
            f.close()
        return(lines)

    @staticmethod
    def convertSecondsToUptime(nbSeconds):
        intervals = (
            ('days', 86400),    # 60 * 60 * 24
            ('hours', 3600),    # 60 * 60
            ('minutes', 60),
            ('seconds', 1),
        )
        result = []
        nbSec = int(nbSeconds)
        for name, count in intervals:
            value = nbSec // count
            if value:
                nbSec -= value * count
                if value <= 1:
                    name = name.rstrip('s')
                result.append("{} {}".format(value, name))
        return ', '.join(result)
