from immutable import List, Map, set, append, remove, pop, add, toPython
from datastore import Datastore
import json

getState, setState, updateState, subscribe = Datastore(Map({
	'players': Map(),
	'matches': List(),
	'current': None
}))

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

def getPlayer(address):
	return getState()['players'][address]

def getAllPlayers():
	return getState()['players']

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
		json.dump(list(toPython(getAllPlayers()).values()), file, indent='\t')

if __name__ == '__main__':
	updateState(addPlayer('RANDOM', ('lo', 3000), ['LUR', 'LRG']))
	updateState(addToPlayer(('lo', 3000), 'points', 10))
	updateState(changePlayerStatus(('lo', 3000), 'prout'))
	print(toPython(getAllPlayers()))