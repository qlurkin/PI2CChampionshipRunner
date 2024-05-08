import asyncio
import logging
import socket
import time

from jsonStream import FetchError, fetch
from status import ClientStatus

log = logging.getLogger("utils")


class PingError(Exception):
    pass


async def ping(client):
    try:
        log.info("Ping {}:{}".format(client.ip, client.port))
        response, _ = await fetch(client, {"request": "ping"}, timeout=0.1, retries=1)
        try:
            if response["response"] != "pong":
                raise PingError("Not a Pong")
        except KeyError as e:
            raise PingError("Key '{}' Missing".format(e))

        client.status = ClientStatus.READY
        return True
    except (OSError, PingError, FetchError) as e:
        log.error(f"Ping Failed {client.ip}:{client.port} ({type(e).__name__}: {e})")
        client.status = ClientStatus.LOST
        return False


def clock(fps=60, period=None):
    if period is None:
        period = 1.0 / fps
    frameStart = time.time()

    async def tic():
        nonlocal frameStart
        frameTime = time.time() - frameStart
        await asyncio.sleep(max(period - frameTime, 0))
        frameStart = time.time()

    return tic


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(("10.254.254.254", 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = "127.0.0.1"
    finally:
        s.close()
    return IP
