from utils import clock
from state import State, MatchStatus, ClientStatus
import asyncio
from match import runMatch
from utils import ping
from logs import getLogger

log = getLogger('championship')

async def rescueClients():
    for client in State.clients.values():
        if client.status == ClientStatus.LOST:
            if await ping(client):
                client.status = ClientStatus.READY

async def runAMatch(Game, tempo):
    for match in State.matches:
        if match.status == MatchStatus.PENDING:
            clients = State.getClients(match)
            if all([client.status == ClientStatus.READY for client in clients]):
                if all([not client.busy for client in clients]):
                    if all(await asyncio.gather(*[ping(client) for client in clients])):
                        for client in clients:
                            client.busy = True
                        match.task = asyncio.create_task(runMatch(Game, match, tempo))

async def awaitAMatch():
    for match in State.matches:
        if match.task is not None and match.task.done():
                try:
                    await match.task
                except Exception as e:
                    log.info(e)
                finally:
                    for client in State.getClients(match):
                        client.busy = False
                    match.task = None
                    log.debug('Handled: {}'.format(match))
                    log.info('Remaining: {}/{}'.format(State.remainingMatches, State.matchCount))

async def championship(Game, tempo):
    log.info('Championship Task Started')
    tic = clock(5)
    while True:
        await tic()
        await runAMatch(Game, tempo)
        await awaitAMatch()
        await rescueClients()