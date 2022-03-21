from datetime import datetime
import os
from state import Match, State
import logging
import sys

date = datetime.now()

consoleFormatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')

fileFormatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s')

matchFileFormatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')

LOGS_FOLDER = 'logs'

def getDateStr():
    return date.strftime("%d-%m-%Y_%H:%M:%S")

if not os.path.exists(LOGS_FOLDER):
        os.mkdir(LOGS_FOLDER)

mainLogFilename = os.path.join(LOGS_FOLDER, getDateStr()+'.log')

def getMainLogFilename():
    return mainLogFilename

def getMatchFilename(match: Match):
    folder = os.path.join(LOGS_FOLDER, getDateStr())
    if not os.path.exists(folder):
        os.mkdir(folder)
    return os.path.join(folder, '{}.log'.format(match).replace(' ', '_'))

def getLogger(name):
    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)

    consoleHandler = logging.StreamHandler(sys.stdout)
    consoleHandler.setLevel(logging.INFO)
    consoleHandler.setFormatter(consoleFormatter)

    fileHandler = logging.FileHandler(mainLogFilename)
    fileHandler.setLevel(logging.INFO)
    fileHandler.setFormatter(fileFormatter)

    log.addHandler(consoleHandler)
    log.addHandler(fileHandler)

    return log

def getMatchLogger(match):
    log = logging.getLogger(str(match))
    log.setLevel(logging.DEBUG)

    consoleHandler = logging.StreamHandler(sys.stdout)
    consoleHandler.setLevel(logging.INFO)
    consoleHandler.setFormatter(consoleFormatter)

    fileHandler = logging.FileHandler(getMatchFilename(match))
    fileHandler.setLevel(logging.DEBUG)
    fileHandler.setFormatter(fileFormatter)

    log.addHandler(consoleHandler)
    log.addHandler(fileHandler)

    return log
