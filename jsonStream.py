import json
import asyncio
import time
from logs import getLogger
from status import ClientStatus

log = getLogger('network')

class NotAJSONObject(Exception):
    pass

class FetchError(Exception):
    pass

class ReadError(Exception):
    pass

async def readJSON(reader: asyncio.StreamReader):
    message = ''
    data = ''
    while True:
        await asyncio.sleep(0)
        chunk = await reader.read(100)
        if len(chunk) == 0:
            raise ReadError('Distant socket closed')
        message += chunk.decode('utf8')
    
        if len(message) > 0 and message[0] != '{':
            raise NotAJSONObject('Received message is not a JSON Object')
        try:
            data = json.loads(message)
            break
        except json.JSONDecodeError:
            pass
    return data

async def writeJSON(writer: asyncio.StreamWriter, obj):
    message = json.dumps(obj)
    if message[0] != '{':
        raise NotAJSONObject('sendJSON support only JSON Object Type')
    message = message.encode('utf8')
    writer.write(message)
    await writer.drain()

async def fetch(client, request, baseTime = 0.25, retries=10, timeout=10.0):
    try:
        for i in range(retries):
            try:
                coro = asyncio.open_connection(client.ip, client.port)#, happy_eyeballs_delay=0.25)
                reader, writer = await asyncio.wait_for(coro, baseTime*(i+1))
                break
            except asyncio.TimeoutError:
                log.debug('Connection take too long. Retry({})...'.format(i+1))
            except OSError as e:
                log.debug('Connection error: {}. Retry({})...'.format(e, i+1))
        else:
            error = "Unable to Open Connection to {}:{}".format(client.ip, client.port)
            log.error(error)
            raise FetchError(error)
        coro = writeJSON(writer, request)
        await asyncio.wait_for(coro, timeout=timeout)
        
        start = time.time()
        
        coro = readJSON(reader)
        response = await asyncio.wait_for(coro, timeout=timeout)
        responseTime = time.time() - start
        writer.close()
        await writer.wait_closed()
        return response, responseTime
    except (OSError, FetchError, asyncio.TimeoutError, ReadError) as e:
        client.status = ClientStatus.LOST
        raise FetchError(str(e))

