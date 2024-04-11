import asyncio

from jsonStream import readJSON, writeJSON
from logs import getLogger
from state import State, StateError
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
                raise InscriptionError(
                    f'Request "{request['request']}" Unsupported'
                )
        except KeyError as e:
            raise InscriptionError(f'Key "{e}" Missing')

        log.info(f'Subscription received from {ip}:{port}')

        try:
            client = await State.addClient(
                name=request['name'],
                port=request['port'],
                matricules=frozenset(map(str,request['matricules'])),
                ip=ip
            )
        except KeyError as e:
            raise InscriptionError(f'Key "{e}" Missing')
        except StateError as e:
            raise InscriptionError(e)
        except Exception as e:
            raise InscriptionError(str(e))

        log.info(f'Pending client: {client.name} ({client.ip}:{client.port})')
        await writeJSON(writer, {'response': 'ok'})
        asyncio.create_task(pingInOneSecond(client))
    except InscriptionError as e:
        log.error(e)
        await writeJSON(writer, {'response': 'error', 'error': str(e)})
    finally:
        writer.close()
        await writer.wait_closed()


async def inscription(port):
    log.info(f'Inscription Task Started. Listen on port {port}')
    await asyncio.start_server(processClient, '0.0.0.0', port)
