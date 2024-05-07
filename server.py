import argparse
import asyncio
import importlib
import socket

from championship import championship, matchAwaiter, rescuer
from inscription import inscription
from logs import getLogger
from state import dumpState
from ui import ui

log = getLogger("server")


async def main(gameName: str, port: int, tempo: float, parall: bool):
    log.info("Game Server For {}".format(gameName.capitalize()))
    try:
        IPAddr = socket.gethostbyname(socket.gethostname())
    except OSError:
        IPAddr = "unknown"

    Game = importlib.import_module("games.{}.game".format(gameName)).Game
    render = importlib.import_module("games.{}.render".format(gameName)).render
    inscriptionTask = asyncio.create_task(inscription(port))
    championshipTask = asyncio.create_task(championship(Game, tempo, parall))
    stateDumperTask = asyncio.create_task(dumpState())
    rescuerTask = asyncio.create_task(rescuer())
    matchAwaiterTask = asyncio.create_task(matchAwaiter())

    await ui(gameName, render, IPAddr, port)

    inscriptionTask.cancel()
    try:
        await inscriptionTask
    except asyncio.CancelledError:
        log.info("Inscription Task Stopped")

    championshipTask.cancel()
    try:
        await championshipTask
    except asyncio.CancelledError:
        log.info("Championship Task Stopped")

    stateDumperTask.cancel()
    try:
        await stateDumperTask
    except asyncio.CancelledError:
        log.info("State Dumper Task Stopped")

    rescuerTask.cancel()
    try:
        await rescuerTask
    except asyncio.CancelledError:
        log.info("Rescuer Task Stopped")

    matchAwaiterTask.cancel()
    try:
        await matchAwaiterTask
    except asyncio.CancelledError:
        log.info("Match awaiter Task Stopped")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("gameName", help="The name of the game")
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        help="The port the server use to listen for subscription",
        default=3000,
    )
    parser.add_argument(
        "-t",
        "--tempo",
        type=float,
        help="value in second. Each move will be, at least, visible during this time.",
        default=0.3,
    )
    parser.add_argument(
        "--parall",
        action=argparse.BooleanOptionalAction,
        help="Don't run match in parallele",
        default=True,
    )
    args = parser.parse_args()

    asyncio.run(main(args.gameName, args.port, args.tempo, args.parall))
