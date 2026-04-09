import json
import asyncio
import time
from logs import getLogger
from status import ClientStatus
import struct

log = getLogger("network")


class NotAJSONObject(Exception):
    pass


class FetchError(Exception):
    pass


class ReadError(Exception):
    pass


class WriteError(Exception):
    pass


async def readJSON(reader: asyncio.StreamReader):
    chunks = []
    data = ""
    received = 0

    buffer = await reader.read(4)
    if len(buffer) == 0:
        raise ReadError("Distant socket closed")
    total = struct.unpack("I", buffer)[0]

    while received < total:
        await asyncio.sleep(0)
        chunk = await reader.read(1024)
        if len(chunk) == 0:
            raise ReadError("Distant socket closed")
        received += len(chunk)
        chunks.append(chunk)

    try:
        data = json.loads(b"".join(chunks).decode("utf8"))
    except json.JSONDecodeError as e:
        raise ReadError(str(e))
    except UnicodeDecodeError as e:
        raise ReadError(str(e))

    return data


async def writeJSON(writer: asyncio.StreamWriter, obj):
    try:
        message = json.dumps(obj)
    except (ValueError, TypeError) as e:
        raise WriteError(str(e))

    try:
        data = message.encode("utf8")
    except UnicodeEncodeError as e:
        raise WriteError(str(e))

    size = struct.pack("I", len(data))
    writer.write(size)
    await writer.drain()
    writer.write(data)
    await writer.drain()


async def fetch(client, request, baseTime=0.25, retries=10, timeout=10.0):
    try:
        for i in range(retries):
            try:
                coro = asyncio.open_connection(
                    client.ip, client.port
                )  # , happy_eyeballs_delay=0.25)
                reader, writer = await asyncio.wait_for(coro, baseTime * (i + 1))
                break
            except TimeoutError:
                log.debug("Connection take too long. Retry({})...".format(i + 1))
            except OSError as e:
                log.debug("Connection error: {}. Retry({})...".format(e, i + 1))
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
    except (OSError, FetchError, TimeoutError, ReadError) as e:
        client.status = ClientStatus.LOST
        raise FetchError(str(e))
