import asyncio
from jsonStream import readJSON, writeJSON
import logging
import time
from jsonStream import fetch
from state import ClientStatus

log = logging.getLogger('server')

class PingError(Exception):
    pass

async def ping(client):
    try:
        log.info('Ping {}:{}'.format(client.ip, client.port))
        response, responseTime = await fetch(client, {'request': 'ping'})
        try:
            if response['response'] != 'pong':
                raise PingError('Not a Pong')
        except KeyError as e:
            raise PingError('Key \'{}\' Missing'.format(e))

        client.status = ClientStatus.READY
        return True
    except (OSError, PingError) as e:
        log.error(f'Ping Failed {client.ip}:{client.port} ({type(e).__name__}: {e})')
        client.status = ClientStatus.LOST
        return False

def clock(fps):
    frameStart = time.time()
    async def tic():
        nonlocal frameStart
        frameTime = time.time() - frameStart
        await asyncio.sleep(max(1.0/fps - frameTime, 0))
        frameStart = time.time()
    return tic

