import logging
import os
import re
import sys
import unicodedata
from datetime import datetime

date = datetime.now()

consoleFormatter = logging.Formatter("%(levelname)s:%(name)s:%(message)s")

fileFormatter = logging.Formatter("%(asctime)s:%(levelname)s:%(name)s:%(message)s")

matchFileFormatter = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")

LOGS_FOLDER = "logs"


def slugify(value, allow_unicode=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
    else:
        value = (
            unicodedata.normalize("NFKD", value)
            .encode("ascii", "ignore")
            .decode("ascii")
        )
    value = re.sub(r"[^\w\s-]", "", value.lower())
    return re.sub(r"[-\s]+", "-", value).strip("-_")


def getDateStr():
    return date.strftime("%d-%m-%Y_%Hh%M.%Ss")


if not os.path.exists(LOGS_FOLDER):
    os.mkdir(LOGS_FOLDER)

mainLogFilename = os.path.join(LOGS_FOLDER, getDateStr() + ".log")
stateFilename = os.path.join(LOGS_FOLDER, getDateStr() + ".json")


def getMainLogFilename():
    return mainLogFilename


def getMatchFilename(match):
    folder = os.path.join(LOGS_FOLDER, getDateStr())
    if not os.path.exists(folder):
        os.mkdir(folder)
    return os.path.join(folder, "{}.log".format(slugify(match)))


def getLogger(name):
    log = logging.getLogger(name)
    if len(log.handlers) == 0:
        log.setLevel(logging.DEBUG)

        consoleHandler = logging.StreamHandler(sys.stdout)
        consoleHandler.setLevel(logging.INFO)
        consoleHandler.setFormatter(consoleFormatter)

        fileHandler = logging.FileHandler(mainLogFilename, encoding="utf8")
        fileHandler.setLevel(logging.INFO)
        fileHandler.setFormatter(fileFormatter)

        log.addHandler(consoleHandler)
        log.addHandler(fileHandler)

    return log


def getMatchLogger(match):
    log = logging.getLogger(str(match))

    while log.hasHandlers():
        log.removeHandler(log.handlers[0])

    log.setLevel(logging.DEBUG)

    consoleHandler = logging.StreamHandler(sys.stdout)
    consoleHandler.setLevel(logging.INFO)
    consoleHandler.setFormatter(consoleFormatter)

    fileHandler = logging.FileHandler(
        getMatchFilename(match), mode="w", encoding="utf8"
    )
    fileHandler.setLevel(logging.DEBUG)
    fileHandler.setFormatter(fileFormatter)

    log.addHandler(consoleHandler)
    log.addHandler(fileHandler)

    return log
