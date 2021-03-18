from immutable import List, Map, set, append, remove, pop, add, toPython
from datastore import Datastore
import json
import time
from chat import postChat
from jsonNetwork import fetch
from games import game
from threading import Thread, Timer

getState, setState, updateState, subscribe = Datastore(Map({
	'players': Map(),
	'matches': List(),
	'matchState': None
}))

hooks = {
	'matchEnd': []
}

def hookRegister(hook, fun):
	hooks[hook] = fun

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

def popMatch(callback):
	def fun(state):
		if len(state['matches']) > 1:
			return state.update('matches', pop(0, callback))
		callback(None)
		return state
	return fun

def getPlayer(state, address):
	return state['players'][address]

def getAllPlayers(state):
	return List(state['players'].values())

def updatePlayer(address, pfun):
	def sfun(state):
		return state.update('players',
			lambda players: players.update(address, pfun))
	return sfun

def addToPlayer(address, key, value):
	def fun(state):
		return updatePlayer(address, lambda player: player.update(key, add(value)))(state)
	return fun

def matchWin(addresses, winner):
	def fun(state):
		for address in addresses:
			state = addToPlayer(address, 'matchCount', 1)(state)
		state = addToPlayer(address, 'points', 3)(state)
		return state
	return fun

def matchDraw(addresses):
	def fun(state):
		for address in addresses:
			state = addToPlayer(address, 'matchCount', 1)(state)
			state = addToPlayer(address, 'points', 1)(state)
		return state
	return fun

def addBadMoves(address, count):
	def fun(state):
		return addToPlayer(address, 'badMoves', count)(state)
	return fun

def changePlayerStatus(address, status):
	def fun(state):
		return updatePlayer(address, lambda player: player.set('status', status))(state)
	return fun


@subscribe
def save(state):
	with open('data.json', 'w', encoding='utf8') as file:
		json.dump(toPython(getAllPlayers(state)), file, indent='\t')

def setMatchState(matchState):
	def fun(state):
		return state.set('matchState', matchState)
	return fun


def Championship(Game):
	running = True

	def postMatchState(matchState):
		updateState(setMatchState(matchState))
		time.sleep(0.5)

	def playMatch(addresses):
		if addresses is None:
			time.sleep(1)
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
				updatePlayer(matchWin(addresses, winner))
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
		while running:
			updateState(popMatch(playMatch))
			__runHook('matchEnd')
	
	championshipThread = Thread(target=run, daemon=True)
	championshipThread.start()

	def stop():
		nonlocal running
		running = False
		championshipThread.join()

	return stop

if __name__ == '__main__':
	pass