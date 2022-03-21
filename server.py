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
from logs import getLogger

log = getLogger('server')

async def main(gameName: str, port: int):
    #log_slow_callbacks.enable(0.5)
    log.info('Game Server For {}'.format(gameName.capitalize()))

    Game = importlib.import_module('games.{}.game'.format(gameName)).Game
    inscriptionTask = asyncio.create_task(inscription(port))
    championshipTask = asyncio.create_task(championship(Game))

    await ui()

    inscriptionTask.cancel()
    log.info('Inscription Task Stopped')
    championshipTask.cancel()
    log.info('Championship Task Stopped')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('gameName', help='The name of the game')
    parser.add_argument('-p', '--port', help='The port the server use to listen for subscription', default=3000)
    args = parser.parse_args()

    asyncio.run(main(args.gameName, args.port))