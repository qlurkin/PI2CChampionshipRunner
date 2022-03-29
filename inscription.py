import asyncio
from mmap import PROT_READ
from jsonStream import readJSON, writeJSON
from state import State, Client, StateError
from logs import getLogger
from utils import ping

log = getLogger('inscription')

class InscriptionError(Exception):
    pass

async def pingInOneSecond(client):
    await asyncio.sleep(1)
    if await ping(client):
        log.info('Client \'{}\' Fully Subscribed'.format(client.name))

async def processClient(reader, writer):
    request = await readJSON(reader)
    ip, port = writer.get_extra_info('peername')

    try:
        try:
            if request['request'] != 'subscribe':
                raise InscriptionError('Request \'{}\' Unsupported')
        except KeyError as e:
            raise InscriptionError('Key \'{}\' Missing'.format(e))

        log.info('Subscription received from {}:{}'.format(ip, port))

        try:
            client = Client(
                name=request['name'],
                port=request['port'],
                matricules=set(request['matricules']),
                ip=ip
            )
        except KeyError as e:
            raise InscriptionError('Key \'{}\' Missing'.format(e))

        try:
            State.addClient(client)
        except StateError as e:
            raise InscriptionError(e)

        log.info('Pending client: {} ({}:{})'.format(client.name, client.ip, client.port))
        await writeJSON(writer, {'response': 'ok'})
        asyncio.create_task(pingInOneSecond(client))
    except InscriptionError as e:
        log.error(e)
        await writeJSON(writer, {'response': 'error', 'error': e})
    finally:
        writer.close()
        await writer.wait_closed()

async def inscription(port):
    log.info('Inscription Task Started')
    await asyncio.start_server(processClient, '0.0.0.0', port)

