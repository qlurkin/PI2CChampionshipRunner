from dataclasses import dataclass
from typing import Any
from enum import Enum

class StateError(Exception):
    pass

class ClientStatus(Enum):
    PENDING = 1
    READY = 2
    LOST = 3

class MatchStatus(Enum):
    PENDING = 1
    RUNNING = 2
    DONE = 3

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
class Move:
    client: str
    move: Any

@dataclass
class Match:
    clients: list
    moves: list
    status: MatchStatus = MatchStatus.PENDING
    winner: str = None
    task = None
    state = None

    def __init__(self, client1: Client, client2: Client):
        self.clients = [client1.name, client2.name]
        self.moves = []

    def __str__(self):
        return '{} VS {}'.format(*self.clients)

@dataclass
class _State:
    clients: dict
    matches: list

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