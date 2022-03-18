import logging
from utils import clock
from state import State, MatchStatus, ClientStatus
import asyncio
from match import runMatch
from utils import ping

log = logging.getLogger('server')

async def runAMatch(Game):
    for match in State.matches:
        if match.status == MatchStatus.PENDING:
            clients = State.getClients(match)
            if all([client.status == ClientStatus.READY for client in clients]):
                if all([not client.busy for client in clients]):
                    log.info('coucou')
                    if all(await asyncio.gather(*[ping(client) for client in clients])):
                        match.status = MatchStatus.RUNNING
                        for client in clients:
                            client.busy = True
                        match.task = asyncio.create_task(runMatch(Game, match))

async def championship(Game):
    log.info('Championship Task Started')
    tic = clock(5)
    while True:
        await tic()
        await runAMatch(Game)