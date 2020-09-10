import glob
import time
import sys
import os
import re
import importlib
import threading
import traceback
import socket
import select
import json
import time
from pympler import muppy
from pympler import summary
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import EVENT_SCHEDULER_STARTED, EVENT_SCHEDULER_PAUSED, EVENT_SCHEDULER_RESUMED, EVENT_JOB_EXECUTED, EVENT_JOB_ERROR, EVENT_JOB_MISSED, EVENT_JOB_MAX_INSTANCES, JobExecutionEvent, SchedulerEvent
from utils.functions import Functions
from os import listdir
from superWattPlugins.abstractClassSuperWattMetrics import AbstractClassSuperWattMetrics
from utils.superWattConfiguration import superWattConfiguration
from utils.superWattNetworkServices import superWattNetworkServices
from superWattPlugins.abstractClassSuperWattConnector import AbstractClassSuperWattConnector
from superWattPlugins.serialConnector import SerialConnector 
from superWattPlugins.serialConnector4pylontech import SerialConnector4pylontech
nbJobsFired = {'good': 0,
               'failed': 0,
               'missed': 0
               }
hashJobsFired = {}

daemonUptime = time.time()
schedulerUptime = time.time()


def checkParameter(args):
    Functions.log(
        "INF", "Entering in checkParameter #parameters=" + str(len(args)), "CORE")
    if (len(args) == 1):
        Functions.log(
            "DEAD", "At least provide one parameter : Configuration file for scheduling metrics picking interval", "CORE")
        return 0
    return 1

def serviceCommandProcess(commandE, scheduler, opt, metrixList):
    optData = ""
    command = ""
    try:
        (command, optData) = commandE.split(":")
    except Exception as err:
        command = commandE
    metrixServiceAnswer = {"metrixServiceAnswer":
                           {"operation": command}}

    Functions.log(
        "INF", "Running treatement for service command " + str(command), "CORE")

    metrixServiceAnswer["metrixServiceAnswer"]["retCode"] = 0
    if command == "reloadConf":
        Functions.log("INF", "Reloading configuration file", "CORE")
        metrixServiceAnswer["metrixServiceAnswer"]["message"] = "Configuration file reloaded"
        opt['command'] = 'reloadConf'

    if command == "printJobs":
        Functions.log("INF", "Printing jobs in scheduler table", "CORE")
        try:
            jobList = scheduler.get_jobs()
        except Exception as err:
            Functions.log("ERR", str(err), "SCHEDULER")
            metrixServiceAnswer["metrixServiceAnswer"]["retCode"] = "1"
            metrixServiceAnswer["metrixServiceAnswer"]["message"] = "Jobs list not retreived"
        else:
            metrixServiceAnswer["metrixServiceAnswer"]["message"] = ""
            for job in jobList:
                metrixServiceAnswer["metrixServiceAnswer"]["message"] += job.id + \
                    ":"+str(scheduler.get_job(job.id))+"; "

    if command == "internalMemStat":
        Functions.log("INF", "Printing internal memories stat", "CORE")
        all_objects = muppy.get_objects()
        size = len(all_objects)/1024
        Functions.log("INF", "Weight of internal objects : " +
                      str(size) + " MB", 'CORE')
        sum1 = summary.summarize(all_objects)
        summary.print_(sum1)
        metrixServiceAnswer["metrixServiceAnswer"]["message"] = "Summary of internal object weight dumped to stdout"

    if command == "schedulerStatus":
        Functions.log("INF", "Scheduler status", "CORE")
        status = scheduler.state
        Functions.log("INF", "sceduler status code is :"+str(status), "CORE")
        message = "Scheduler status is "
        if status == 0:
            message += "state_stopped"
        if status == 1:
            message += "state_running"
        if status == 2:
            message += "state_paused"
        metrixServiceAnswer["metrixServiceAnswer"]["message"] = message

    if command == "pauseJobs":
        Functions.log("INF", "Pausing jobs", "CORE")
        try:
            scheduler.pause()
        except Exception as err:
            Functions.log("ERR", str(err), "SCHEDULER")
            metrixServiceAnswer["metrixServiceAnswer"]["retCode"] = "1"
            metrixServiceAnswer["metrixServiceAnswer"]["message"] = "Jobs not paused"
        else:
            metrixServiceAnswer["metrixServiceAnswer"]["message"] = "Jobs paused"

    if command == "resumeJobs":
        Functions.log("INF", "Resuming jobs", "CORE")
        try:
            scheduler.resume()
        except Exception as err:
            Functions.log("ERR", str(err), "SCHEDULER")
            metrixServiceAnswer["metrixServiceAnswer"]["retCode"] = "1"
            metrixServiceAnswer["metrixServiceAnswer"]["message"] = "Jobs not resumed"
        else:
            metrixServiceAnswer["metrixServiceAnswer"]["message"] = "Jobs resumed"

    if command == "ping":
        Functions.log("INF", "Answering to ping request", "CORE")
        upTm = Functions.convertSecondsToUptime(time.time()-daemonUptime)
        metrixServiceAnswer["metrixServiceAnswer"]["message"] = "Reply to ping request. Daemon uptime : " + \
            str(upTm)

    if command == "statistics":
        Functions.log("INF", "Answering to statistics request", "CORE")
        metrixServiceAnswer["metrixServiceAnswer"]["message"] = nbJobsFired

    if command == "detailledStatistics":
        Functions.log(
            "INF", "Answering to detailled statistics request", "CORE")
        metrixServiceAnswer["metrixServiceAnswer"]["message"] = hashJobsFired

    if command == "getLastPayloadSent":
        Functions.log(
            "INF", "Answering to last payload sent request", "CORE")
        hashRes = {}
        if optData:
            metrixServiceAnswer["metrixServiceAnswer"]["data"] = optData
            if optData in metrixList:
                hashRes[optData] = metrixList[optData].getLastPayloadSent()
            else:
                metrixServiceAnswer["metrixServiceAnswer"]["retCode"] = "1"
                hashRes[optData] = "unknown metrics. No history for this"
        else:
            for metric in metrixList:
                hashRes[metric] = metrixList[metric].getLastPayloadSent()
        metrixServiceAnswer["metrixServiceAnswer"]["message"] = hashRes

    if command == "setLogLevel":
        Functions.log(
            "INF", "Answering to LogLevel change request", "CORE")
        if optData:
            metrixServiceAnswer["metrixServiceAnswer"]["data"] = optData
            if(Functions.setLogLevel(optData)):
                metrixServiceAnswer["metrixServiceAnswer"]["message"] = "Log level changed to '"+optData+"'"
            else:
                metrixServiceAnswer["metrixServiceAnswer"]["retCode"] = "1"
                metrixServiceAnswer["metrixServiceAnswer"]["message"] = "Log level '" + \
                    optData+"' unknown. Not changed"

    if command == "stopDaemon":
        Functions.log("INF", "Stopping daemon jobs", "CORE")
        Functions.log("INF", "Scheduler pause", "SCHEDULER")
        try:
            scheduler.pause()
        except Exception as err:
            Functions.log("ERR", str(err), "SCHEDULER")
        Functions.log("INF", "Scheduler shutdown", "SCHEDULER")
        try:
            scheduler.shutdown()
        except Exception as err:
            Functions.log("ERR", str(err), "SCHEDULER")
            metrixServiceAnswer["metrixServiceAnswer"]["retCode"] = "1"
            metrixServiceAnswer["metrixServiceAnswer"]["message"] = "Unable to stop daemon"
        else:
            Functions.log("INF", "Scheduler stopped", "SCHEDULER")
            metrixServiceAnswer["metrixServiceAnswer"]["message"] = "Daemon stopping in progress"
            opt['command'] = 'stopDaemon'
    return json.dumps(metrixServiceAnswer)


def my_listener(event):
    if isinstance(event, SchedulerEvent):
        if event.code == EVENT_SCHEDULER_STARTED:
            Functions.log("INF", "Scheduler has started", "SCHEDULER")
            schedulerUptime = time.time()
        if event.code == EVENT_SCHEDULER_PAUSED:
            schedulerUptime = 0.0
            Functions.log("INF", "Scheduler has paused", "SCHEDULER")
        if event.code == EVENT_SCHEDULER_RESUMED:
            schedulerUptime = time.time()
            Functions.log("INF", "Scheduler has resumed", "SCHEDULER")
    if isinstance(event, JobExecutionEvent):
        hashJobsFired[event.job_id]['totalFired'] += 1
        if event.code == EVENT_JOB_EXECUTED:
            Functions.log(
                "INF", "The job has runned successfully", "SCHEDULER")
            nbJobsFired['good'] += 1
            hashJobsFired[event.job_id]['good'] += 1
        if event.code == EVENT_JOB_ERROR:
            Functions.log("INF", "The job has crashed", "SCHEDULER")
            nbJobsFired['failed'] += 1
            hashJobsFired[event.job_id]['failed'] += 1
        if event.code == EVENT_JOB_MISSED:
            Functions.log("INF", "The job has been missed", "SCHEDULER")
            nbJobsFired['missed'] += 1
            hashJobsFired[event.job_id]['missed'] += 1


def loadSuperWattMetricsPlugins(influxDbUrl, influxDbPort, influxDbName, metricsPlugInPath, serialCon, serialCon4Pylontech):
    importlib.import_module('superWattPlugins')
    metricList = {}
    Functions.log("INF", "Loading module superWattPlugins in progress", "CORE")
    for file in glob.glob(metricsPlugInPath+"/M*.py"):
        moduleName = os.path.basename(file.replace(".py", ""))
        try:
            Functions.log("INF", "Loading module " + moduleName, "CORE")
            mod=importlib.import_module('.'+moduleName,package="superWattPlugins")
            Functions.log("INF", "End loading metrix/" + moduleName, "CORE")
            Functions.log(
                "INF", "Trying dynamic instantiation " + moduleName, "CORE")
            aClass=getattr(mod, moduleName)
            if moduleName=="M_pylontech" or moduleName=="M_pylontech2":
               instanceMetrix = aClass( influxDbUrl, influxDbPort, influxDbName,serialCon4Pylontech)
            else :
               instanceMetrix = aClass( influxDbUrl, influxDbPort, influxDbName,serialCon)
            if isinstance(instanceMetrix, AbstractClassSuperWattMetrics):
                Functions.log("INF", "Module " + moduleName +
                              " is an instance of AbstractClassSuperWattMetrics, Loading object", "CORE")
                metricList[moduleName] = instanceMetrix
                hashStatus = {'good': 0,
                              'failed': 0,
                              'missed': 0,
                              'totalFired': 0
                              }
                hashJobsFired[moduleName] = hashStatus
            else:
                Functions.log("ERR", "Module " + moduleName +
                              " isn't an instance of AbstractClassMetrix", "CORE")
        except Exception as err:
            Functions.log("ERR", "Couldn't instantiate " +
                          moduleName + " error " + str(err), "CORE")
            traceback.print_tb(err.__traceback__)
    return metricList

def addJobsToScheduler(metricsL, schedul, metrixC):
    for collectM in metricsL:
        Functions.log("INF", "Adding "+collectM+" to scheduler", "SCHEDULER")
        obj = metricsL[collectM]
        schedul.add_job(obj.run, 'interval', seconds=metrixC.getSamplingFor(
            collectM), max_instances=metrixC.getMaxRunFor(collectM), id=collectM)
        Functions.log("INF", "Setting interval of "+str(
            metrixC.getSamplingFor(collectM)) + " seconds for "+collectM, "SCHEDULER")
        Functions.log("INF", "Setting maximum simultaneous run of " +
                      str(metrixC.getMaxRunFor(collectM)) + " for "+collectM, "SCHEDULER")


def main():
    Functions.log("INF", "Starting superWatt Meter", "CORE")
    if checkParameter(sys.argv) == 0:
        exit(0)
    Functions.log(
        "INF", "Listing modules depending of parameters received " + sys.argv[1:][0], "CORE")
    superWattConfig = superWattConfiguration(sys.argv[1:][0])

    superWattConfig.loadConfiguration()
    superWattConfig.checkConfiguration()
    serialCon=SerialConnector()
    serialCon.defineInterfaceParameters(superWattConfig.getSerialConProp())
    serialCon.openConnection()
    Functions.log("INF", "Test connection to superWatt", "CORE")
    mesgSuperWatt=serialCon.testConnection()
    Functions.log("INF", mesgSuperWatt, "CORE")
    serialCon4pylontech=SerialConnector4pylontech()
    serialCon4pylontech.defineInterfaceParameters(superWattConfig.getSerialConProp4pylontech())
    serialCon4pylontech.openConnection()
    Functions.log("INF", "Test connection to pylontech", "CORE")
    mesgPylontech=serialCon4pylontech.testConnection()
    serialCon4pylontech.closeConnection()
    Functions.log("INF", mesgPylontech, "CORE")
    myNetworkService = superWattNetworkServices(superWattConfig.getDaemonServicePort(), superWattConfig.getDaemonMaxCon())
    metricsList = loadSuperWattMetricsPlugins( superWattConfig.getInfluxDbUrl(), superWattConfig.getInfluxDbPort(), superWattConfig.getInfluxDbName(), superWattConfig.getMetrixPlugInPath(),serialCon,serialCon4pylontech)
    Functions.log("INF", "Testing serial connection to superwatt says :"+mesgSuperWatt, "CORE")
 
    scheduler = BackgroundScheduler({
        'apscheduler.executors.default': {
            'class': 'apscheduler.executors.pool:ThreadPoolExecutor',
            'max_workers': superWattConfig.getMaxThreadForScheduler()
        },
        'apscheduler.executors.processpool': {
            'type': 'processpool',
            'max_workers': superWattConfig.getMaxForkForScheduler()
        }})

    addJobsToScheduler(metricsList, scheduler, superWattConfig)
    Functions.log("INF", "Starting scheduler", "SCHEDULER")
    scheduler.add_listener(my_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR | EVENT_JOB_MISSED |
                           EVENT_SCHEDULER_STARTED | EVENT_SCHEDULER_PAUSED | EVENT_SCHEDULER_RESUMED)
    scheduler.start()
    optOperation = {'command': 'noFired'}
    try:
        while True:
            myNetworkService.manageNetworkService()
            while True:
                message = myNetworkService.getServicesMessages()
                if not len(message):
                    break
                badQuery = 0
                sock, mesg = message
                cde = myNetworkService.decodeNetworkMessage(
                    mesg, metrixConfig.getServicesCommandList())
                if not cde:
                    myNetworkService.badServiceAnswer(sock)
                else:
                    stop = 0
                    mess = serviceCommandProcess(
                        cde, scheduler, optOperation, metricsList)
                    if optOperation['command'] == 'stopDaemon':
                        time.sleep(3)
                        myNetworkService.goodServiceAnswer(sock, mess)
                        Functions.log("INF", "Stopping daemon", "CORE")
                        exit(0)
                    if optOperation['command'] == 'reloadConf':
                        optOperation['command'] = 'not Fired'
                        loadConfiguration(metrixConfig)
                        Functions.log("INF", "Pausing scheduler jobs", "CORE")
                        try:
                            scheduler.pause()
                        except Exception as err:
                            Functions.log("ERR", str(err), "SCHEDULER")
                            mServiceAnswer["metrixServiceAnswer"]["retCode"] = "1"
                            mServiceAnswer["metrixServiceAnswer"]["message"] = "can not pause scheduler"
                            myNetworkService.goodServiceAnswer(
                                sock, json.dumps(mServiceAnswer))
                        else:
                            try:
                                jobList = scheduler.get_jobs()
                            except Exception as err:
                                Functions.log("ERR", str(err), "SCHEDULER")
                                mServiceAnswer["metrixServiceAnswer"]["retCode"] = "1"
                                mServiceAnswer["metrixServiceAnswer"]["message"] = "can not retreive job list"
                                myNetworkService.goodServiceAnswer(
                                    sock, json.dumps(mServiceAnswer))
                            else:
                                jobRemoveOk = 1
                                for job in jobList:
                                    Functions.log(
                                        "INF", "Removing job "+str(job.id), "SCHEDULER")
                                    try:
                                        scheduler.remove_job(job.id)
                                    except Exception as err:
                                        Functions.log(
                                            "INF", "Can not remove job id"+str(job.id), "SCHEDULER")
                                        mServiceAnswer["metrixServiceAnswer"]["retCode"] = "1"
                                        mServiceAnswer["metrixServiceAnswer"]["message"] = "can not remove a job from scheduler"
                                        myNetworkService.goodServiceAnswer(
                                            sock, json.dumps(mServiceAnswer))
                                        jobRemoveOk = 0
                                if jobRemoveOk:
                                    Functions.log(
                                        "INF", "Reloading jobs into scheduler", "SCHEDULER")
                                    addJobsToScheduler(
                                        metricsList, scheduler, metrixConfig)
                                    Functions.log(
                                        "INF", "Resuming scheduler jobs", "SCHEDULER")
                                    try:
                                        scheduler.resume()
                                    except Exception as err:
                                        Functions.log(
                                            "INF", "Can not resume scheduler jobs", "SCHEDULER")
                                        mServiceAnswer["metrixServiceAnswer"]["retCode"] = "1"
                                        mServiceAnswer["metrixServiceAnswer"]["message"] = "can not resume scheduler jobs"
                                        myNetworkService.goodServiceAnswer(
                                            sock, json.dumps(mServiceAnswer))
                                    else:
                                        myNetworkService.goodServiceAnswer(
                                            sock, mess)
                    else:
                        myNetworkService.goodServiceAnswer(sock, mess)
            time.sleep(0.1)
    except (KeyboardInterrupt, SystemExit):
        # Not strictly necessary if daemonic mode is enabled but should be done if possible
        try:
            scheduler.shutdown()
        except Exception as err:
            pass


if __name__ == "__main__":
    main()
