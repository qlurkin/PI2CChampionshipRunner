from dataclasses import dataclass
from typing import Any
from utils import clock
import asyncio
from logs import getLogger, stateFilename, date
from status import ClientStatus, MatchStatus
import json
import jsonpickle
from datetime import datetime

log = getLogger('state')

class StateError(Exception):
    pass

@dataclass
class Client:
    name: str
    port: int
    ip: str
    matricules: list
    status: ClientStatus = ClientStatus.PENDING
    busy: bool = False
    badMoves: int = 0
    matchCount: int = 0
    points: int = 0

    def __str__(self):
        return self.name

@dataclass
class Match:
    clients: list
    moves = 0
    start = None
    end = None
    status: MatchStatus = MatchStatus.PENDING
    winner: str = None
    task = None
    state = None

    def __init__(self, client1: Client, client2: Client):
        self.clients = [client1.name, client2.name]

    def __str__(self):
        return '{} VS {}'.format(*self.clients)

    def __getstate__(self):
        D = dict(self.__dict__)
        D['task'] = None
        return D

@dataclass
class _State:
    clients: dict
    matches: list
    date: datetime = date

    def addClient(self, client: Client):
        if client.name in self.clients and self.clients[client.name].matricules != client.matricules:
            raise StateError('Name \'{}\' Already Used'.format(client.name))
        for other in self.clients.values():
            self.matches.append(Match(client, other))
            self.matches.append(Match(other, client))
        self.clients[client.name] = client

    def getClients(self, match: Match):
        return [self.clients[name] for name in match.clients]

    @property
    def remainingMatches(self):
        return len(list(filter(lambda match: match.status != MatchStatus.DONE, self.matches)))

    @property
    def matchCount(self):
        return len(self.matches)


State = _State(clients = {}, matches = [])
log.info('State Created')

async def dumpState():
    log.info('State Dumper Started')
    tic = clock(1)
    while True:
        await tic()
        with open(stateFilename, 'w', encoding='utf8') as file:
            file.write(jsonpickle.encode(State))

