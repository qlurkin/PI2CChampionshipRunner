import asyncio
from jsonStream import FetchError, readJSON, writeJSON
import logging
import time
from jsonStream import fetch
from status import ClientStatus

log = logging.getLogger('utils')

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
    except (OSError, PingError, FetchError) as e:
        log.error(f'Ping Failed {client.ip}:{client.port} ({type(e).__name__}: {e})')
        client.status = ClientStatus.LOST
        return False

def clock(fps=60, period=None):
    if period is None:
        period = 1.0/fps
    frameStart = time.time()
    async def tic():
        nonlocal frameStart
        frameTime = time.time() - frameStart
        await asyncio.sleep(max(period - frameTime, 0))
        frameStart = time.time()
    return tic

