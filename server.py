import asyncio
from inscription import inscription
from championship import championship
from ui import ui
import logging
import sys
from state import State
import importlib
import argparse

log = logging.getLogger('server')
log.setLevel(logging.INFO)
log.addHandler(logging.StreamHandler(sys.stdout))

async def main(gameName, port):
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