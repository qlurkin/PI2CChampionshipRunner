import math
from immutable import List, Map, insertAtRandomPlace, setItem, append, remove, add, toPython
from datastore import Datastore
import json
import time
from chat import postChat
from jsonNetwork import fetch, Timeout
from games import game
from threading import Thread
from match import postMatchState
from datetime import datetime
import random

timeStr = datetime.now().strftime('%Y-%m-%d_%Hh%M')

getState, updateState, subscribe = Datastore(Map({
	'players': Map(),
	'matches': List(),
	'matchResults': List()
}))

def loadPreviousData(filename):
	with open(filename) as file:
		data = json.load(file)

hooks = {
	'matchEnd': []
}

def hookRegister(hook, fun):
	hooks[hook].append(fun)

def __runHook(hook):
	for fun in hooks[hook]:
		fun()

def addMatch(addresses):
	def addMatch(state):
		return state.update('matches', insertAtRandomPlace(addresses))
	return addMatch

def addPlayer(name, address, matricules, points=0, badMoves=0, matchCount=0, status='offline'):
	
	player = Map({
		'name': name,
		'status': status,
		'address': address,
		'points': points,
		'badMoves': badMoves,
		'matchCount': matchCount,
		'matricules': matricules
	})

	def addPlayer(state):
		if address in state['players']:
			state = updatePlayer(address, lambda player: player.set('name', name).set('status', status).set('matricules', matricules))(state)
		else:
			for opponent in state['players']:
				players = [address, opponent]
				random.shuffle(players)
				state = addMatch(tuple(players))(state)
			state = state.update('players', setItem(address, player))
		return state
	return addPlayer

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

def addMatchResult(addresses, winner, badMoves, moveCount, playerTimes, totalTime):
	def addMatchResult(state):
		#players = [state['players'][addresse]['name'] for addresse in addresses]
		return state.update('matchResults', append(Map({
			'players': addresses,
			'badMoves': badMoves,
			'winner': winner,
			'moveCount': moveCount,
			'playerTimes': playerTimes,
			'totalTime': totalTime
		})))
	return addMatchResult

def alreadyPlayed(addresses):
	for match in getState()['matchResults']:
		if set(match['players']) == set(addresses):
			return True
	return False

@subscribe
def save(state):
	with open('data_{}.json'.format(timeStr), 'w', encoding='utf8') as file:
		json.dump({
			'players': toPython(getAllPlayers(state)),
			'results': toPython(state['matchResults'])
		}, file, indent='\t')

def Championship(Game, matchCount):
	running = True

	def playMatch(addresses):
		players = List()
		for address in addresses:
			players = players.append(getPlayer(getState(), address))
		lives = [3, 3]
		errors = [[], []]
		badMoves = lambda : [3 - l for l in lives]

		def kill(player, msg, state, move):
			postChat('Admin', msg)
			errors[player].append({
				'message': msg,
				'state': state,
				'move': move
			})
			lives[player] -= 1

		def matchResult(winner):
			for i, count in enumerate(badMoves()):
				updateState(addBadMoves(addresses[i], count))
			if winner is None:
				updateState(matchDraw(addresses))
			else:
				updateState(matchWin(addresses, winner))
			updateState(addMatchResult(addresses, winner, badMoves(), moveCount, playerTimes, time.time() - totalStart))
			postMatchState(None)

		matchState, next = Game(list(map(lambda player: player['name'], players)))
		matchState['current'] = 0
		postMatchState(matchState)

		postChat('Admin', '{} VS {}'.format(players[0]['name'], players[1]['name']))
		playerTimes = [0, 0]
		moveCount = 0
		totalStart = time.time()
		try:
			while all([l != 0 for l in lives]):
				if not running:
					return
				print('Request move from {}'.format(players[matchState['current']]['name']))
				try:
					request = {
						'request': 'play',
						'lives': lives[matchState['current']],
						'errors': errors[matchState['current']],
						'state': matchState
					}
					start = time.time()
					response = fetch(players[matchState['current']]['address'], request, timeout=3.1)
					playerTime = time.time() - start
					if 'message' in response:
						postChat(players[matchState['current']]['name'], response['message'])
					if response['response'] == 'move':
						moveCount += 1
						playerTimes[matchState['current']] += playerTime
						print('{} play ({}s):\n{}'.format(players[matchState['current']]['name'], playerTime, response['move']))
						try:
							matchState = next(matchState, response['move'])
							postMatchState(matchState)
						except game.BadMove as e:
							kill(matchState['current'], 'This is a Bad Move. ' + str(e), matchState, response['move'])
					if response['response'] == 'giveup':
						postChat('Admin', '{} give up'.format(players[matchState['current']]['name']))
						raise game.GameWin((matchState['current']+1)%2, matchState)
				except Timeout:
					kill(matchState['current'], 'You take too long to respond', matchState, None)
				except OSError:
					kill(matchState['current'], '{} unavailable'.format(players[matchState['current']]['name']), matchState, None)
			postChat('Admin', '{} has done too many Bad Moves'.format(players[matchState['current']]['name']))
			matchResult((matchState['current']+1)%2)
		except game.GameWin as e:
			postChat('Admin', 'Game Over: {} win the game'.format(players[e.winner]['name']))
			postMatchState(e.state)
			matchResult(e.winner)
		except game.GameDraw as e:
			postChat('Admin', str(e))
			postMatchState(e.state)
			matchResult(None)

	def run():
		print("Start Championship")
		count = 0
		while running and count < matchCount:
			matches = getState()['matches']
			if len(matches) > 0:
				addresses = matches[0]
				updateState(removeFirstMatch())
				if alreadyPlayed(addresses):
					continue
				if all(map(lambda address: getPlayer(getState(), address)['status'] == 'online', addresses)):
					playMatch(addresses)
					count += 1
				else:
					postChat('Admin', 'Some player are offline. Report Match')
					updateState(addMatch(addresses))
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
