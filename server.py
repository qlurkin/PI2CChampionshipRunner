import socket
from jsonNetwork import sendJSON, receiveJSON, NotAJSONObject
from threading import Thread, Timer, Lock
import time
from tictactoe import Game
import importlib
import game
import sys
import json

inscriptionSocket = socket.socket()
inscriptionSocket.bind(('0.0.0.0', 3000))
inscriptionSocket.settimeout(1)
inscriptionSocket.listen()

running = True

clients = {}

match = []
matchLock = Lock()

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

def checkAllClients():
	for address in clients:
		checkClient(address)

def subscribe(address, name, matricules):
	status = checkClient(address)
	if status == 'online':
		with matchLock:
			if address not in clients:
				for opponent in clients:
					match.append([address, opponent])
					match.append([opponent, address])

				clients[address] = {
					'address': address,
					'points': 0,
					'badMoves': 0,
					'matchCount': 0,
					'matricules': matricules
				}

			clients[address]['name'] = name
			clients[address]['status'] = status
			
		print('MATCH LIST:\n{}'.format('\n'.join(map(lambda address: '{}:{}'.format(address[0], address[1]), match))))


def runMatch(playersAddress):
	players = []
	for i in range(len(playersAddress)):
		players.append(clients[playersAddress[i]])

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

def processRequest(client, address):
	print('request from', address)
	try:
		data = receiveJSON(client)
		
		if data['request'] != 'subscribe':
			raise ValueError('Unknown request \'{}\''.format(data['request']))

		clientAddress = (address[0], int(data['port']))
	
		print('Subscription received for {} with address {}'.format(data['name'], clientAddress))

		if any([not isinstance(matricule, str) for matricule in data['matricules']]):
			raise TypeError("Matricules must be strings")
		
		sendJSON(client, {
			'response': 'ok'
		})

		Timer(1, subscribe, [clientAddress, data['name'], data['matricules']]).start()

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


def processClients():
	while running:
		try:
			client, address = inscriptionSocket.accept()
			processRequest(client, address)
			client.close()
		except socket.timeout:
			pass


if __name__ == '__main__':
	listenThread = Thread(target=processClients, daemon=True)
	listenThread.start()

	Game = importlib.import_module(sys.argv[1]).Game

	try:
		print('Ctrl-C to stop')
		while True:
			players = None
			with matchLock:
				if len(match) > 0:
					players = match[0]
					match[0:1] = []
			if players is not None:
				winner, badMoves = runMatch(players)
				for player, count in enumerate(badMoves):
					clients[players[player]]['badMoves'] += count
					clients[players[player]]['matchCount'] += 1
					if winner is None:
						clients[players[player]]['points'] += 1
					elif winner == player:
						clients[players[player]]['points'] += 3
				with open('data.json', 'w', encoding='utf8') as file:
					json.dump(list(clients.values()), file, indent='\t')
			time.sleep(1)
	except KeyboardInterrupt:
		print('bye')

	running = False
	listenThread.join()
