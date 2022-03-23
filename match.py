from dataclasses import dataclass
from jsonStream import FetchError, fetch
from games import game
from state import State, Match, Client, Chat, Message
import asyncio
import time
from logs import getLogger, getMatchLogger
from status import ClientStatus

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

    log.info('Match Started')
    match.start = time.time()
    players = [Player(client, i) for i, client in enumerate(State.getClients(match))]
    winner = None
    matchState, next = Game(match.clients)
    matchState['current'] = 0
    match.state = matchState
    chat = Chat()
    match.chat = chat

    def kill(player, msg, move):
        log.warning(msg)
        player.kill(msg, matchState, move)
        chat.addMessage(Message(name="Admin", message=msg))

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
                current.client.status = ClientStatus.READY

                if 'message' in response:
                    chat.addMessage(Message(name=str(current), message=response['message']))
            
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
                    msg = '{} Give Up'.format(current)
                    log.info(msg)
                    chat.addMessage(Message(name="Admin", message=msg))
                    raise game.GameWin(other.index, matchState)
            except FetchError:
                kill(current, '{} unavailable. Wait for {} seconds'.format(current, RETRY_TIME), None)
                await asyncio.sleep(RETRY_TIME)
        
        msg = '{} has done too many Bad Moves'.format(current)
        log.warning(msg)
        chat.addMessage(Message(name="Admin", message=msg))
        raise game.GameWin(other.index, matchState)

    except game.GameWin as e:
        winner = players[e.winner]
        match.winner = str(winner)
        msg = 'Match Done. {} Won'.format(winner.client.name)
        log.info(msg)
        chat.addMessage(Message(name="Admin", message=msg))

    except game.GameDraw as e:
        winner = None
        msg = 'Match Done with no winner'
        log.info(msg)
        chat.addMessage(Message(name="Admin", message=msg))

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
