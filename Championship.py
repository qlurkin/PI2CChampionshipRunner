from immutable import List, Map, set, append, remove, pop, add, toPython
from datastore import Datastore
import json
import time
from chat import postChat
from jsonNetwork import fetch
from games import game
from threading import Thread, Timer

getState, updateState, subscribe = Datastore(Map({
	'players': Map(),
	'matches': List(),
	'matchState': None,
	'matchResults': List()
}))

hooks = {
	'matchEnd': []
}

def hookRegister(hook, fun):
	hooks[hook].append(fun)

def __runHook(hook):
	for fun in hooks[hook]:
		fun()

def addPlayer(name, address, matricules):
	
	player = Map({
		'name': name,
		'status': 'online',
		'address': address,
		'points': 0,
		'badMoves': 0,
		'matchCount': 0,
		'matricules': matricules
	})

	def fun(state):
		for opponent in state['players']:
			state = state.update('matches', append((address, opponent)))
			state = state.update('matches', append((opponent, address)))
		state = state.update('players', set(address, player))
		return state
	
	return fun

def removeFirstMatch():
	def removeFirstMatch(state):
		return state.update('matches', remove(0))
	return removeFirstMatch

def getPlayer(state, address):
	return state['players'][address]

def getAllPlayers(state):
	return List(state['players'].values())

def updatePlayer(address, pfun):
	def updatePlayer(state):
		return state.update('players',
			lambda players: players.update(address, pfun))
	return updatePlayer

def addToPlayer(address, key, value):
	def addToPlayer(state):
		return updatePlayer(address, lambda player: player.update(key, add(value)))(state)
	return addToPlayer

def matchWin(addresses, winner):
	def matchWin(state):
		for address in addresses:
			state = addToPlayer(address, 'matchCount', 1)(state)
		state = addToPlayer(addresses[winner], 'points', 3)(state)
		return state
	return matchWin

def matchDraw(addresses):
	def matchDraw(state):
		for address in addresses:
			state = addToPlayer(address, 'matchCount', 1)(state)
			state = addToPlayer(address, 'points', 1)(state)
		return state
	return matchDraw

def addBadMoves(address, count):
	def addBadMoves(state):
		return addToPlayer(address, 'badMoves', count)(state)
	return addBadMoves

def changePlayerStatus(address, status):
	def changePlayerStatus(state):
		return updatePlayer(address, lambda player: player.set('status', status))(state)
	return changePlayerStatus

def addMatchResult(addresses, winner, badMoves):
	def addMatchResult(state):
		return state.update('matchResults', append(Map({
			'players': addresses,
			'badMoves': badMoves,
			'winner': winner
		})))
	return addMatchResult


@subscribe
def save(state):
	with open('data.json', 'w', encoding='utf8') as file:
		json.dump({
			'players': toPython(getAllPlayers(state)),
			'results': toPython(state['matchResults'])
		}, file, indent='\t')

def setMatchState(matchState):
	def setMatchState(state):
		return state.set('matchState', matchState)
	return setMatchState


def Championship(Game):
	running = True

	def postMatchState(matchState):
		updateState(setMatchState(matchState))
		time.sleep(0.5)

	def playMatch(addresses):
		players = List()
		for address in addresses:
			players = players.append(getPlayer(getState(), address))
		lives = [3, 3]
		badMoves = lambda : [3 - l for l in lives]

		def matchResult(winner):
			for i, count in enumerate(badMoves()):
				updateState(addBadMoves(addresses[i], count))
			if winner is None:
				updateState(matchDraw(addresses))
			else:
				updateState(matchWin(addresses, winner))
			updateState(addMatchResult(addresses, winner, badMoves()))
			postMatchState(None)

		matchState, next = Game(list(map(lambda player: player['name'], players)))
		matchState['current'] = 0
		postMatchState(matchState)

		postChat('Admin', '{} VS {}'.format(players[0]['name'], players[1]['name']))

		try:
			while all([l != 0 for l in lives]):
				print('Request move from {}'.format(players[matchState['current']]['name']))
				response = fetch(players[matchState['current']]['address'], {
					'request': 'play',
					'lives': lives[matchState['current']],
					'state': matchState
				}, timeout=3)
				if 'message' in response:
					postChat(players[matchState['current']]['name'], response['message'])
				if response['response'] == 'move':
					print('{} play:\n{}'.format(players[matchState['current']]['name'], response['move']))
					try:
						matchState = next(matchState, response['move'])
						postMatchState(matchState)
					except game.BadMove:
						print('Bad Move')
						postChat('Admin', 'This is a Bad Move')
						lives[matchState['current']] -= 1
				if response['response'] == 'giveup':
					postChat('Admin', '{} give up'.format(players[matchState['current']]['name']))
					raise game.GameWin((matchState['current']+1)%2, matchState)
			print(players[matchState['current']]['name'], 'has done too many Bad Moves')
			matchResult((matchState['current']+1)%2)
		except game.GameWin as e:
			print('Winner', players[e.winner]['name'])
			postChat('Admin', 'Winner {}'.format(players[matchState['current']]['name']))
			postMatchState(e.state)
			matchResult(e.winner)
		except game.GameDraw as e:
			print('Draw')
			postChat('Admin', 'Draw')
			postMatchState(e.state)
			matchResult(None)

	def run():
		print("Start Championship")
		while running:
			matches = getState()['matches']
			if len(matches) > 0:
				addresses = matches[0]
				updateState(removeFirstMatch())
				playMatch(addresses)
				__runHook('matchEnd')
			else:
				time.sleep(1)
	
	championshipThread = Thread(target=run, daemon=True)
	championshipThread.start()

	def stop():
		nonlocal running
		running = False
		championshipThread.join()

	return stop

if __name__ == '__main__':
	pass