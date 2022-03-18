import json
import asyncio

class NotAJSONObject(Exception):
    pass

async def readJSON(reader: asyncio.StreamReader):
    message = ''
    data = ''
    while True:
        chunk = await reader.read(100)
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

async def fetch(client, request):
    reader, writer = await asyncio.open_connection(client.ip, client.port)
    await writeJSON(writer, request)
    response = await readJSON(reader)
    writer.close()
    await writer.wait_closed()
    return response

