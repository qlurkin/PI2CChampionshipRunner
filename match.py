from dataclasses import dataclass
from typing import Any
from jsonStream import fetch

from state import State, Match, MatchStatus, Client
import asyncio
import logging

log = logging.getLogger('server')

@dataclass
class Error:
    message: str
    matchState: Any
    move: Any

@dataclass
class Player:
    client: Client
    errors: list

    def __init__(self, client: Client):
        self.client = client
        self.errors = []

    @property
    def lives(self):
        return 3 - self.badMoves

    @property
    def badMoves(self):
        return len(self.errors)

    def kill(self, msg, matchState, move):
        self.errors.append(Error(
            message = msg,
            matchState=matchState,
            move=move
        ))

async def runMatch(Game: callable, match: Match):
    log.info('Match {} VS {} Started'.format(*match.clients))
    players = [Player(client) for client in State.getClients(match)]
    winner = None
    matchState, next = Game(match.clients)
    matchState['current'] = 0
    match.state = matchState

    def current():
        return players[matchState['current']]

    while all([player.lives != 0 for player in players]):
        log.info('Request move from {}'.format(current().client.name))

        request = {}
        
        response = await fetch(current().client, request)

    match.status = MatchStatus.DONE
    for player in players:
        client = player.client
        client.busy = False
        client.matchCount += 1
        client.badMoves += player.badMoves
        if winner is None:
            client.points += 1
        elif winner is player:
            client.points += 3

    if winner is None:
        log.info('Match {} VS {} Done with no winner'.format(*match.clients))
    else:
        log.info('Match {} VS {} Done. {} Won'.format(*match.clients, winner.client.name))
