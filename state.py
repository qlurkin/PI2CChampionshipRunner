import asyncio
from dataclasses import dataclass
from typing import Optional
from utils import clock
from logs import getLogger, stateFilename, date
from status import ClientStatus, MatchStatus
import jsonpickle
from datetime import datetime
import random

log = getLogger('state')


class StateError(Exception):
    pass


@dataclass
class Client:
    name: str
    port: int
    ip: str
    matricules: set
    status: ClientStatus = ClientStatus.PENDING
    busy: bool = False
    badMoves: int = 0
    matchCount: int = 0
    points: int = 0

    def __str__(self):
        return self.name


@dataclass
class Message:
    name: str
    message: str


class Chat:
    def __init__(self):
        self.messages = []

    def addMessage(self, msg: Message):
        self.messages.append(msg)
        if len(self.messages) > 10:
            self.messages.pop(0)


@dataclass
class Match:
    clients: list
    badMoves: list
    points: list
    moves: int = 0
    start: float | None = None
    end: float | None = None
    status: MatchStatus = MatchStatus.PENDING
    winner: str | None = None
    task: asyncio.Task | None = None
    state: Optional['_State'] = None
    chat: Chat | None = None

    def __init__(self, client1: Client, client2: Client):
        self.clients = [client1.name, client2.name]
        self.badMoves = [0, 0]
        self.points = [0, 0]

    def __str__(self):
        return '{} VS {}'.format(*self.clients)

    def __getstate__(self):
        D = dict(self.__dict__)
        D['task'] = None
        D['chat'] = None
        return D

    async def reset(self):
        if self.task is not None:
            task = self.task
            task.cancel()
            self.task = None
            try:
                await task
            except asyncio.CancelledError as e:
                assert self.chat is not None, 'Chat is None'
                self.chat.addMessage(Message('Admin', str(e)))
            finally:
                for client in State.getClients(self):
                    client.busy = False
        if self.status == MatchStatus.DONE:
            for i, client in enumerate(State.getClients(self)):
                client.matchCount -= 1
                client.badMoves -= self.badMoves[i]
                client.points -= self.points[i]
        self.moves = 0
        self.start = None
        self.end = None
        self.status = MatchStatus.PENDING
        self.winner = None
        self.task = None
        self.state = None
        self.chat = None
        self.badMoves = [0, 0]
        self.points = [0, 0]
        log.info('Match {} Reset'.format(self))

    async def stop(self):
        if self.status == MatchStatus.RUNNING:
            pass


class ClientNotFoundError(Exception):
    pass


@dataclass
class _State:
    clients: dict
    matches: list
    date: datetime = date

    def getClientByMatricules(self, matricules: set):
        for client in self.clients.values():
            if client.matricules == matricules:
                return client
        raise ClientNotFoundError()

    async def removeClient(self, name):
        for match in list(self.matches):
            if name in match.clients:
                if match.status != MatchStatus.PENDING:
                    await match.reset()
                self.matches.remove(match)
        self.clients.pop(name)
        log.info('Client {} Removed'.format(name))

    async def addClient(self, client: Client):
        try:
            oldClient = self.getClientByMatricules(client.matricules)
            client.badMoves = oldClient.badMoves
            client.matchCount = oldClient.matchCount
            client.points = oldClient.points
            if oldClient.name != client.name:
                await self.removeClient(oldClient.name)
                await self.addClient(client)
        except ClientNotFoundError:
            if client.name in self.clients:
                raise StateError('Name \'{}\' Already Used'.format(
                    client.name
                ))
            for other in self.clients.values():
                players = [other, client]
                random.shuffle(players)
                self.matches.append(Match(*players))
            self.clients[client.name] = client

    def getClients(self, match: Match):
        return [self.clients[name] for name in match.clients]

    @property
    def remainingMatches(self):
        return len(list(filter(
            lambda match: match.status != MatchStatus.DONE,
            self.matches
        )))

    @property
    def runningMatches(self):
        return len(list(filter(
            lambda match: match.task is not None,
            self.matches
        )))

    @property
    def matchCount(self):
        return len(self.matches)


State = _State(clients={}, matches=[])
log.info('State Created')


async def dumpState():
    log.info('State Dumper Started')
    tic = clock(1)
    while True:
        await tic()
        with open(stateFilename, 'w', encoding='utf8') as file:
            file.write(str(jsonpickle.encode(State)))
