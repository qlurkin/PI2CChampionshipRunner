import asyncio

from logs import getLogger
from match import runMatch
from state import ClientStatus, MatchStatus, State
from utils import clock, ping

log = getLogger("championship")


async def rescueClients():
    clients = list(State.clients.values())
    for client in clients:
        if client.status == ClientStatus.LOST:
            if await ping(client):
                client.status = ClientStatus.READY


async def runAMatch(Game, tempo, parall):
    matches = list(State.matches)
    for match in matches:
        if (not parall) and State.runningMatches > 0:
            return
        if match.status == MatchStatus.PENDING:
            clients = match.clients
            if all([client.status == ClientStatus.READY for client in clients]):
                if all([not client.busy for client in clients]):
                    if all(await asyncio.gather(*[ping(client) for client in clients])):
                        for client in clients:
                            client.busy = True
                        match.task = asyncio.create_task(runMatch(Game, match, tempo))
                    return


async def awaitAMatch():
    matches = list(State.matches)
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
    tic = clock(5)
    while True:
        await tic()
        await runAMatch(Game, tempo, parall)
        await awaitAMatch()
        await rescueClients()
