from copy import copy
import socket

from jsonNetwork import sendJSON, receiveJSON, NotAJSONObject
from threading import Thread, Timer
import time
import importlib
from games import game
import sys
import clients
import pygame
import copy
from chat import postChat


def fetch(address, data):
	'''
		Request response from address. Data is included in the request
	'''
	s = socket.socket()
	s.connect(address)
	sendJSON(s, data)
	response = receiveJSON(s)
	return response


def checkClient(address):
	'''
		Ping client
	'''
	print('checking client {}'.format(address))
	try:
		response = fetch(address, {
			'request': 'ping'
		})
		if response['response'] == 'pong':
			status = 'online'
		else:
			raise ValueError()
	except:
		status = 'lost'

	print(status)
	return status

def checkAllClient():
	for client in clients.getAll():
		status = checkClient(client['address'])
		clients.changeStatus(client['address'], status)


def finalizeSubscription(address, name, matricules):
	'''
		Add client if successfully pinged
	'''
	status = checkClient(address)
	if status == 'online':
		clients.add(address, name, matricules)


def runMatch(Game, addresses, postState):
	players = []
	for i in range(len(addresses)):
		players.append(clients.get(addresses[i]))

	state, next = Game(list(map(lambda P: P['name'], players)))
	state['current'] = 0
	postState(state)

	print('{} VS {}'.format(players[0]['name'], players[1]['name']))
	postChat('Admin', '{} VS {}'.format(players[0]['name'], players[1]['name']))

	lives = [3, 3]
	badMoves = lambda : [3 - l for l in lives]
	try:
		while all([l != 0 for l in lives]):
			print('Request move from {}'.format(players[state['current']]['name']))
			response = fetch(players[state['current']]['address'], {
				'request': 'play',
				'lives': lives[state['current']],
				'state': state
			})
			if response['response'] == 'move':
				print('{} play:\n{}'.format(players[state['current']]['name'], response['move']))
				if 'message' in response:
					postChat(players[state['current']]['name'], response['message'])
				try:
					state = next(state, response['move'])
					postState(state)
				except game.BadMove:
					print('Bad Move')
					postChat('Admin', 'This is a Bad Move')
					lives[state['current']] -= 1
			if response['response'] == 'giveup':
				postChat('Admin', '{} give up'.format(players[state['current']]['name']))
				raise game.GameWin((state['current']+1)%2, state)
		print(players[state['current']]['name'], 'has done too many Bad Moves')
		return (state['current']+1)%2, badMoves()
	except game.GameWin as e:
		print('Winner', players[e.winner]['name'])
		postChat('Admin', 'Winner {}'.format(players[state['current']]['name']))
		postState(e.state)
		return e.winner, badMoves()
	except game.GameDraw as e:
		print('Draw')
		postChat('Admin', 'Draw')
		postState(e.state)
		return None, badMoves()


def startSubscription(client, address, request):
	'''
	Because client may be single threaded, he may start listening to request
	after sending his substriction. We wait for 1 second before pinging him
	'''
	clientAddress = (address[0], int(request['port']))
	
	print('Subscription received for {} with address {}'.format(request['name'], clientAddress))

	if any([not isinstance(matricule, str) for matricule in request['matricules']]):
		raise TypeError("Matricules must be strings")
	
	sendJSON(client, {
		'response': 'ok'
	})

	Timer(1, finalizeSubscription, [clientAddress, request['name'], request['matricules']]).start()


def processRequest(client, address):
	'''
		Route request to request handlers
	'''
	print('request from', address)
	try:
		request = receiveJSON(client)
		
		if request['request'] == 'subscribe':
			startSubscription(client, address, request)
		else:
			raise ValueError('Unknown request \'{}\''.format(request['request']))

	except socket.timeout:
		sendJSON(client, {
			'response': 'error',
			'error': 'transmition take too long'
		})
	except NotAJSONObject as e:
		sendJSON(client, {
			'response': 'error',
			'error': str(e)
		})
	except KeyError as e:
		sendJSON(client, {
			'response': 'error',
			'error': 'Missing key {}'.format(str(e))
		})
	except Exception as e:
		sendJSON(client, {
			'response': 'error',
			'error': str(e)
		})


def listenForRequests(port):
	'''
		Start thread to listen to requests.
		Returns a function to stop the thread.
	'''
	running = True
	def processClients():
		with socket.socket() as s:
			s.bind(('0.0.0.0', port))
			s.settimeout(1)
			s.listen()
			print('Listen to', port)
			while running:
				try:
					client, address = s.accept()
					with client:
						processRequest(client, address)
				except socket.timeout:
					pass
	
	listenThread = Thread(target=processClients, daemon=True)
	listenThread.start()

	def stop():
		nonlocal running
		running = False
		listenThread.join()

	return stop

def championship(Game):
	running = True
	state = None

	def postState(newState):
		nonlocal state
		state = copy.deepcopy(newState)
		time.sleep(1)

	def run():
		while running:
			players = clients.getMatch()
			if players is not None:
				winner, badMoves = runMatch(Game, players, postState)
				for player, count in enumerate(badMoves):
					clients.addBadMoves(players[player], count)
				if winner is None:
					clients.matchDraw(players)
				else:
					clients.matchWin(players, winner)
				postState(None)
				checkAllClient()
				clients.save()
			else:
				time.sleep(1)
	
	championshipThread = Thread(target=run, daemon=True)
	championshipThread.start()

	def stop():
		nonlocal running
		running = False
		championshipThread.join()

	def getState():
		return state

	return stop, getState

def formatClient(client):
	return '{}: {}'.format(client['name'], client['points'])

def main(getState, render):
	pygame.init()
	import graphics
	screen = pygame.display.set_mode(graphics.screenSize)
	pygame.display.set_caption('{} Championship'.format(gameName.capitalize()))

	clock = pygame.time.Clock()
	font = pygame.font.Font(None, 36)

	while True:
		clock.tick(60)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				return

		state = getState()
		stateImage = render(state)
		participants = clients.getAll()

		surface = graphics.render(state, participants, stateImage)

		screen.blit(surface, (0, 0))
		pygame.display.flip()


if __name__ == '__main__':
	args = sys.argv[1:]
	port = 3000
	gameName = None
	for arg in args:
		if arg.startswith('-port='):
			port = int(arg[len('-port='):])
		else:
			gameName = arg

	stopSubscriptions = listenForRequests(port)

	Game = importlib.import_module('games.{}.game'.format(gameName)).Game
	render = importlib.import_module('games.{}.render'.format(gameName)).render

	stopChampionship, getState = championship(Game)


	main(getState, render)

	
	stopSubscriptions()
	stopChampionship()
