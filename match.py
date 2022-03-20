from dataclasses import dataclass
from typing import Any
from jsonStream import FetchError, fetch
from games import game
from state import State, Match, MatchStatus, Client
import asyncio
import logging
import sys
from logFilenames import consoleFormatter, getMatchFilename, matchFileFormatter

log = logging.getLogger('server')

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
        self.errors.append({
            'message': msg,
            'state': matchState,
            'move': move
        })

async def runMatch(Game: callable, match: Match):
    log = logging.getLogger(str(match))
    log.setLevel(logging.DEBUG)

    consoleHandler = logging.StreamHandler(sys.stdout)
    consoleHandler.setLevel(logging.DEBUG)
    consoleHandler.setFormatter(consoleFormatter)

    fileHandler = logging.FileHandler(getMatchFilename(match))
    fileHandler.setLevel(logging.INFO)
    fileHandler.setFormatter(matchFileFormatter)

    log.addHandler(consoleHandler)
    log.addHandler(fileHandler)

    log.info('Match Started')
    players = [Player(client) for client in State.getClients(match)]
    winner = None
    matchState, next = Game(match.clients)
    matchState['current'] = 0
    match.state = matchState

    def current():
        return players[matchState['current']]

    def other():
        return players[(matchState['current']+1)%2]

    try:
        while all([player.lives != 0 for player in players]):
            try:
                request = {
                    'request': 'play',
                    'lives': current().lives,
                    'errors': current().errors,
                    'state': matchState
                }
                
                response, responseTime = await fetch(current().client, request)

                if responseTime > 10:
                    current().kill('{} take too long to respond: {}s'.format(current().client.name, responseTime))

                if 'message' in response:
                    pass
            
                if response['response'] == 'move':
                    try:
                        matchState = next(matchState, response['move'])
                    except game.BadMove as e:
                        current().kill('This is a Bad Move. ' + str(e), matchState, response['move'])
                
                if response['response'] == 'giveup':
                    raise game.GameWin((matchState['current']+1)%len(players), matchState)
            except FetchError as e:
                log.info('KILL')
                current().kill('{} unavailable: {}'.format(current().client.name, e), matchState, None)
        
        log.info('{} has done too many Bad Moves'.format(current().client.name))
        winner = other()

    except game.GameWin as e:
        winner = players[e.winner]
        log.info('Match Done. {} Won'.format(winner.client.name))

    except game.GameDraw as e:
        winner = None
        log.info('Match Done with no winner')

    for player in players:
        client = player.client
        client.matchCount += 1
        client.badMoves += player.badMoves
        if winner is None:
            client.points += 1
        elif winner is player:
            client.points += 3
