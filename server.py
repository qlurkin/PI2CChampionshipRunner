import socket
from jsonNetwork import sendJSON, receiveJSON, NotAJSONObject
from threading import Thread, Timer
import time
from tictactoe import Game
import importlib
import game
import sys
import clients


def fetch(address, data):
	s = socket.socket()
	s.connect(address)
	sendJSON(s, data)
	response = receiveJSON(s)
	return response


def checkClient(address):
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


def finalizeSubscription(address, name, matricules):
	status = checkClient(address)
	if status == 'online':
		clients.add(address, name, matricules)


def runMatch(addresses):
	players = []
	for i in range(len(addresses)):
		players.append(clients.get(addresses[i]))

	state, next = Game(list(map(lambda P: P['name'], players)))
	state['current'] = 0

	print('{} VS {}'.format(players[0]['name'], players[1]['name']))

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
				try:
					state = next(state, response['move'])
				except game.BadMove:
					print('Bad Move')
					lives[state['current']] -= 1
		print(players[state['current']]['name'], 'has done too many Bad Moves')
		return (state['current']+1)%2, badMoves()
	except game.GameWin as e:
		print('Winner', players[e.winner]['name'])
		return e.winner, badMoves()
	except game.GameDraw:
		print('Draw')
		return None, badMoves()


def startSubscription(client, address, request):
	clientAddress = (address[0], int(request['port']))
	
	print('Subscription received for {} with address {}'.format(request['name'], clientAddress))

	if any([not isinstance(matricule, str) for matricule in request['matricules']]):
		raise TypeError("Matricules must be strings")
	
	sendJSON(client, {
		'response': 'ok'
	})

	Timer(1, finalizeSubscription, [clientAddress, request['name'], request['matricules']]).start()


def processRequest(client, address):
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
	running = True
	def processClients():
		with socket.socket() as s:
			s.bind(('0.0.0.0', port))
			s.settimeout(1)
			s.listen()
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


if __name__ == '__main__':
	
	stopSubscriptions = listenForRequests(3000)

	Game = importlib.import_module(sys.argv[1]).Game

	try:
		print('Ctrl-C to stop')
		while True:
			players = clients.getMatch()
			if players is not None:
				winner, badMoves = runMatch(players)
				for player, count in enumerate(badMoves):
					clients.addBadMoves(players[player], count)
				if winner is None:
					clients.matchDraw(players)
				else:
					clients.matchWin(players, winner)
				clients.save()
			time.sleep(1)
	except KeyboardInterrupt:
		print('bye')

	
	stopSubscriptions()
