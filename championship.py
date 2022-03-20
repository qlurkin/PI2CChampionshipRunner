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
                    if all(await asyncio.gather(*[ping(client) for client in clients])):
                        match.status = MatchStatus.RUNNING
                        for client in clients:
                            client.busy = True
                        match.task = asyncio.create_task(runMatch(Game, match))
                        match.handled = False

async def awaitAMatch():
    for match in State.matches:
        if match.task is not None and match.task.done():
            if not match.handled:
                try:
                    log.info('Handling {} VS {}'.format(*match.clients))
                    await match.task
                except Exception as e:
                    log.info(e)
                finally:
                    match.status = MatchStatus.DONE
                    for client in State.getClients(match):
                        client.busy = False
                    match.handled = True

async def championship(Game):
    log.info('Championship Task Started')
    tic = clock(5)
    while True:
        #log.info('CHAMPIONSHIP BEFORE TIC')
        await tic()
        #log.info('CHAMPIONSHIP BEFORE RUNAMATCH')
        await runAMatch(Game)
        #log.info('CHAMPIONSHIP BEFORE AWAITAMATCH')
        await awaitAMatch()
        #log.info('CHAMPIONSHIP AFTER AWAITAMATCH')