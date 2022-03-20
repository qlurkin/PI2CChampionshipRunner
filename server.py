import os
#os.environ['PYTHONASYNCIODEBUG'] = '1'
import asyncio
from webbrowser import get
from inscription import inscription
from championship import championship
from ui import ui
import logging
import sys
from state import State
import importlib
import argparse
from aiodebug import log_slow_callbacks
from logFilenames import getMainLogFilename, fileFormatter, consoleFormatter

log = logging.getLogger('server')
log.setLevel(logging.DEBUG)

consoleHandler = logging.StreamHandler(sys.stdout)
consoleHandler.setLevel(logging.DEBUG)
consoleHandler.setFormatter(consoleFormatter)

fileHandler = logging.FileHandler(getMainLogFilename())
fileHandler.setLevel(logging.INFO)
fileHandler.setFormatter(fileFormatter)

log.addHandler(consoleHandler)
log.addHandler(fileHandler)

async def main(gameName, port):
    #log_slow_callbacks.enable(0.5)
    Game = importlib.import_module('games.{}.game'.format(gameName)).Game
    inscriptionTask = asyncio.create_task(inscription(port))
    championshipTask = asyncio.create_task(championship(Game))

    await ui()

    inscriptionTask.cancel()
    championshipTask.cancel()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('gameName', help='The name of the game')
    parser.add_argument('-p', '--port', help='The port the server use to listen for subscription', default=3000)
    args = parser.parse_args()

    asyncio.run(main(args.gameName, args.port))