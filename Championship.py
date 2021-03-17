from immutable import List, Map, setValue, append, remove
from datastore import Datastore

getState, setState, updateState = Datastore(Map({
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
		state = state.update('players', setValue(address, player))
		return state
	
	return fun

def popMatch():
	state = getState()
	matches = state['matches']
	if len(matches) > 0:
		res = matches[0]
		matches = matches[1:]
	state = state.set('matches', matches)
	setState(state)
	return res

def getPlayer(address):
	return getState()['players'][address]

def getAllPlayers():
	return getState()['players']

def matchWin(addresses, winner):
	state = getState()
	
	for address in addresses:
		player = getPlayer(address)
		player = player.set('matchCount', player['matchCount'] + 1)
		state = state['players'].set(address, player)

	player = getPlayer(addresses[winner])
	player = player.set('points', player['points'] + 3)
	state = state['players'].set(addresses[winner], player)
	
	setState(state)

def matchDraw(addresses):
	state = getState()
	
	for address in addresses:
		player = getPlayer(address)
		player = player.set('matchCount', player['matchCount'] + 1)
		player = player.set('points', player['points'] + 1)
		state = state['players'].set(address, player)
	
	setState(state)


