from dataclasses import dataclass
from jsonStream import FetchError, fetch
from games import game
from state import State, Match, Client
import asyncio
import time
from logs import getLogger, getMatchLogger

MOVE_TIME_LIMIT = 10
RETRY_TIME = 5

log = getLogger('match')

@dataclass
class Player:
    client: Client
    errors: list
    index: int

    def __init__(self, client: Client, index):
        self.client = client
        self.errors = []
        self.index = index

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

    def __str__(self):
        return str(self.client)

async def runMatch(Game: callable, match: Match):
    log = getMatchLogger(match)

    def kill(player, msg, move):
        log.warning(msg)
        player.kill(msg, matchState, move)

    log.info('Match Started')
    match.start = time.time()
    players = [Player(client, i) for i, client in enumerate(State.getClients(match))]
    winner = None
    matchState, next = Game(match.clients)
    matchState['current'] = 0
    match.state = matchState

    try:
        while all([player.lives != 0 for player in players]):
            try:
                current = players[matchState['current']]
                other = players[(matchState['current']+1)%2]
                request = {
                    'request': 'play',
                    'lives': current.lives,
                    'errors': current.errors,
                    'state': matchState
                }
                
                response, responseTime = await fetch(current.client, request)

                if 'message' in response:
                    pass
            
                if response['response'] == 'move':
                    move = response['move']
                    log.debug('{} play {}'.format(current, move))
                    try:
                        matchState = next(matchState, move)
                        match.state = matchState
                        match.moves += 1
                        if responseTime > MOVE_TIME_LIMIT:
                            kill(current, '{} take too long to respond: {}s'.format(current, responseTime), move)
                    except game.BadMove as e:
                        kill(current, 'This is a Bad Move. ' + str(e), matchState, move)
                
                if response['response'] == 'giveup':
                    log.info('{} Give Up'.format(current))
                    raise game.GameWin(other.index, matchState)
            except FetchError:
                kill(current, '{} unavailable. Wait for {} seconds'.format(current, RETRY_TIME), matchState, None)
                await asyncio.sleep(RETRY_TIME)
        
        log.warning('{} has done too many Bad Moves'.format(current))
        winner = other

    except game.GameWin as e:
        winner = players[e.winner]
        match.winner = str(winner)
        log.info('Match Done. {} Won'.format(winner.client.name))

    except game.GameDraw as e:
        winner = None
        log.info('Match Done with no winner')

    match.state = None
    match.end = time.time()
    for player in players:
        client = player.client
        client.matchCount += 1
        client.badMoves += player.badMoves
        if winner is None:
            client.points += 1
        elif winner is player:
            client.points += 3
