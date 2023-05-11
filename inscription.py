import asyncio
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
                raise InscriptionError(
                    'Request \'{}\' Unsupported'.format(request['request'])
                )
        except KeyError as e:
            raise InscriptionError('Key \'{}\' Missing'.format(e))

        log.info('Subscription received from {}:{}'.format(ip, port))

        try:
            client = Client(
                name=request['name'],
                port=request['port'],
                matricules=set(map(str,request['matricules'])),
                ip=ip
            )
        except KeyError as e:
            raise InscriptionError('Key \'{}\' Missing'.format(e))
        except Exception as e:
            raise InscriptionError(str(e))

        try:
            await State.addClient(client)
        except StateError as e:
            raise InscriptionError(e)

        log.info('Pending client: {} ({}:{})'.format(
            client.name,
            client.ip,
            client.port
        ))
        await writeJSON(writer, {'response': 'ok'})
        asyncio.create_task(pingInOneSecond(client))
    except InscriptionError as e:
        log.error(e)
        await writeJSON(writer, {'response': 'error', 'error': str(e)})
    finally:
        writer.close()
        await writer.wait_closed()


async def inscription(port):
    log.info('Inscription Task Started. Listen on port {}'.format(port))
    await asyncio.start_server(processClient, '0.0.0.0', port)
