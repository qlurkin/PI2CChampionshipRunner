from datetime import datetime
import os
from state import Match, State
import logging

date = datetime.now()

consoleFormatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')

fileFormatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s')

matchFileFormatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')

def getDateStr():
    return date.strftime("%d-%m-%Y_%H:%M:%S")

def getMainLogFilename():
    return getDateStr()+'.log'

def getMatchFilename(match: Match):
    if not os.path.exists(getDateStr()):
        os.mkdir(getDateStr())
    return os.path.join(getDateStr(), '{}.log'.format(match).replace(' ', '_'))
