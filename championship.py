import asyncio
import random

from logs import getLogger
from match import runMatch
from state import ClientStatus, MatchStatus, State
from utils import clock, ping

log = getLogger("championship")


async def rescueAClients():
    clients = list(State.clients.values())
    random.shuffle(clients)
    for client in clients:
        if client.status == ClientStatus.LOST:
            if await ping(client):
                client.status = ClientStatus.READY
            return


def runAMatch(Game, tempo, parall):
    if (not parall) and State.runningMatches > 0:
        return
    matches = list(State.matches)
    random.shuffle(matches)
    for match in matches:
        if match.status == MatchStatus.PENDING:
            clients = match.clients
            if all([client.status == ClientStatus.READY for client in clients]):
                if all([not client.busy for client in clients]):
                    for client in clients:
                        client.busy = True
                    log.debug("try running {}".format(match))
                    match.task = asyncio.create_task(runMatch(Game, match, tempo))
                    return


async def awaitAMatch():
    matches = list(State.matches)
    random.shuffle(matches)
    for match in matches:
        if match.task is not None and match.task.done():
            try:
                await match.task
            except Exception as e:
                log.info(e)
            finally:
                for client in match.clients:
                    client.busy = False
                match.task = None
                log.debug("Handled: {}".format(match))
                log.info(
                    "Remaining: {}/{}".format(State.remainingMatches, State.matchCount)
                )


async def championship(Game, tempo, parall):
    log.info("Championship Task Started")
    tic = clock(10)
    while True:
        await tic()
        log.debug("try running A match")
        runAMatch(Game, tempo, parall)


async def matchAwaiter():
    log.info("Match Awaiter Task Started")
    tic = clock(10)
    while True:
        await tic()
        log.debug("awaiting a match")
        await awaitAMatch()


async def rescuer():
    log.info("Rescuer Task Started")
    tic = clock(10)
    while True:
        await tic()
        log.debug("try rescueing a client")
        await rescueAClients()
