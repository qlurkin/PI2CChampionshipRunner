import asyncio
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

import json

from inscription import InscriptionError
from logs import date, getLogger, stateFilename
from status import ClientStatus, MatchStatus
from utils import clock

log = getLogger("state")


class StateError(Exception):
    pass


@dataclass
class Client:
    name: str
    port: int
    ip: str
    matricules: frozenset
    status: ClientStatus = ClientStatus.PENDING
    busy: bool = False

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
    clients: list[Client]
    badMoves: list[int]
    moves: int = 0
    start: Optional[float] = None
    end: Optional[float] = None
    status: MatchStatus = MatchStatus.PENDING
    winner: Optional[Client] = None
    task: Optional[asyncio.Task] = None
    state: Optional[Any] = None
    chat: Optional[Chat] = None

    def __init__(self, client1: Client, client2: Client):
        self.clients = [client1, client2]
        self.badMoves = [0, 0]

    def __str__(self):
        return "{} VS {}".format(*[client.name for client in self.clients])

    def __getstate__(self):
        D = dict(self.__dict__)
        D["task"] = None
        D["chat"] = None
        return D

    async def reset(self):
        if self.task is not None:
            task = self.task
            task.cancel()
            self.task = None
            try:
                await task
            except asyncio.CancelledError as e:
                assert self.chat is not None, "Chat is None"
                self.chat.addMessage(Message("Admin", str(e)))
            finally:
                for client in self.clients:
                    client.busy = False
        self.moves = 0
        self.start = None
        self.end = None
        self.status = MatchStatus.PENDING
        self.winner = None
        self.task = None
        self.state = None
        self.chat = None
        self.badMoves = [0, 0]
        log.info("Match {} Reset".format(self))


class ClientNotFoundError(Exception):
    pass


@dataclass
class _State:
    clients: dict[frozenset[str], Client]
    matches: list[Match]
    date: datetime = date

    async def removeClient(self, matricules: frozenset[str]):
        client = self.clients[matricules]
        for match in list(self.matches):
            if client in match.clients:
                if match.status != MatchStatus.PENDING:
                    await match.reset()
                self.matches.remove(match)
        self.clients.pop(matricules)
        log.info("Client {} Removed".format(client.name))

    async def addClient(
        self, name: str, port: int, matricules: frozenset[str], ip: str
    ) -> Client:
        if matricules in self.clients:
            oldClient = self.clients[matricules]
            oldClient.name = name
            oldClient.port = port
            oldClient.ip = ip
            return oldClient
        else:
            names = [c.name for c in self.clients.values()]
            if name in names:
                raise InscriptionError(f"Name '{name}' already used")
            client = Client(name=name, port=port, matricules=matricules, ip=ip)
            for other in self.clients.values():
                # players = [other, client]
                # random.shuffle(players)
                # self.matches.append(Match(*players))
                self.matches.append(Match(client, other))
                self.matches.append(Match(other, client))
            self.clients[client.matricules] = client
            return client

    @property
    def remainingMatches(self) -> int:
        return len(
            list(filter(lambda match: match.status != MatchStatus.DONE, self.matches))
        )

    @property
    def runningMatches(self) -> int:
        return len(list(filter(lambda match: match.task is not None, self.matches)))

    @property
    def matchCount(self):
        return len(self.matches)

    def getPoints(self, client: Client) -> int:
        res = 0
        for match in self.matches:
            if client in match.clients:
                if match.status == MatchStatus.DONE:
                    if match.winner == client:
                        res += 3
                    elif match.winner is None:
                        res += 1
        return res

    def getBadMoves(self, client: Client) -> int:
        res = 0
        for match in self.matches:
            if client in match.clients:
                i = match.clients.index(client)
                res += match.badMoves[i]
        return res

    def getMatchCount(self, client: Client) -> int:
        res = 0
        for match in self.matches:
            if client in match.clients:
                if match.status == MatchStatus.DONE:
                    res += 1
        return res


State = _State(clients={}, matches=[])
log.info("State Created")


async def dumpState():
    log.info("State Dumper Started")
    tic = clock(1)
    while True:
        await tic()
        clients = []
        for client in State.clients.values():
            clients.append({
                "matricules": list(client.matricules),
                "name": client.name,
                "points": State.getPoints(client),
                "bad_moves": State.getBadMoves(client),
                "match_count": State.getMatchCount(client),
            })
        matches = []
        for match in State.matches:
            dumped_match = {
                "clients": [{"name": c.name, "matricules": list(c.matricules)} for c in match.clients],
                "bad_moves": match.badMoves,
                "moves": match.moves,
                "status": match.status.name,
            }

            if match.start is not None and match.end is not None:
                dumped_match["time"] = match.end - match.start

            if match.winner is None:
                dumped_match['winner'] = None
            else:
                dumped_match['winner'] = {"name": match.winner.name, "matricules": list(match.winner.matricules)}

            matches.append(dumped_match)

        with open(stateFilename, "w", encoding="utf8") as file:
            s = {"clients": list(reversed(sorted(clients, key=lambda c: c["points"]))), "matches": matches}
            try:
                to_write = json.dumps(s, indent=2)
                file.write(to_write)
            except Exception as e:
                file.write(str(e))
