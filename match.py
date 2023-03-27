from dataclasses import dataclass
from jsonStream import FetchError, fetch
from games import game
from state import State, Match, Client, Chat, Message
import asyncio
import time
from logs import getLogger, getMatchLogger
from status import ClientStatus, MatchStatus
from utils import clock

MOVE_TIME_LIMIT = 3
RETRY_TIME = 3

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


async def runMatch(Game, match: Match, tempo: float):
    log = getMatchLogger(match)
    match.status = MatchStatus.RUNNING

    log.info('Match Started')
    match.start = time.time()
    players = [Player(client, i) for i, client in enumerate(State.getClients(match))]
    winner = None
    matchState, next = Game(match.clients)
    matchState['current'] = 0
    match.state = matchState
    chat = Chat()
    match.chat = chat
    current = None
    other = None

    def kill(player, msg, move):
        log.warning(msg)
        player.kill(msg, matchState, move)
        chat.addMessage(Message(name="Admin", message=msg))

    try:
        tic = clock(period=tempo)
        while all([player.lives != 0 for player in players]):
            await tic()
            current = players[matchState['current']]
            other = players[(matchState['current']+1)%2]
            try:
                request = {
                    'request': 'play',
                    'lives': current.lives,
                    'errors': current.errors,
                    'state': matchState
                }
                
                response, responseTime = await fetch(current.client, request, timeout=MOVE_TIME_LIMIT*1.1)
                current.client.status = ClientStatus.READY

                if 'message' in response :
                    chat.addMessage(Message(name=str(current), message=str(response['message'])))
            
                if response['response'] == 'move':
                    move = response['move']
                    log.debug('{} play {}'.format(current, move))
                    try:
                        matchState = next(matchState, move)
                        match.state = matchState
                        match.moves += 1
                        if responseTime > MOVE_TIME_LIMIT*1.1:
                            kill(current, '{} take too long to respond: {}s'.format(current, responseTime), move)
                    except game.BadMove as e:
                        kill(current, 'This is a Bad Move. ' + str(e), move)
                
                elif response['response'] == 'giveup':
                    msg = '{} Give Up'.format(current)
                    log.info(msg)
                    chat.addMessage(Message(name="Admin", message=msg))
                    raise game.GameWin(other.index, matchState)

                else:
                    kill(current, 'response[\'response\'] can\'t be {}'.format(response['response']), None)
            except FetchError as e:
                kill(current, '{} unavailable ({}). Wait for {} seconds'.format(current, e, RETRY_TIME), None)
                await asyncio.sleep(RETRY_TIME)
            except (TypeError, KeyError) as e:
                kill(current, 'Error in the turn of {}: {}. Wait for {} seconds'.format(current, e, RETRY_TIME), None)
                await asyncio.sleep(RETRY_TIME)

        assert current is not None
        assert other is not None
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
    for i, player in enumerate(players):
        client = player.client
        client.matchCount += 1
        client.badMoves += player.badMoves
        match.badMoves[i] = player.badMoves
        if winner is None:
            match.points[i] = 1
        elif winner is player:
            match.points[i] = 3
        client.points += match.points[i]
        
    match.status = MatchStatus.DONE
