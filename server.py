import socket
from jsonNetwork import sendJSON, receiveJSON, NotAJSONObject
from threading import Thread, Timer, Lock
import time
from tictactoe import Game
import game

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

def subscribe(address, name):
	status = checkClient(address)
	if status == 'online':
		with matchLock:
			if address not in clients:
				for opponent in clients:
					match.append([address, opponent])
					match.append([opponent, address])

			clients[address] = {
				'name': name,
				'address': address,
				'status': status
			}
			
		print('MATCH LIST:\n{}'.format('\n'.join(map(lambda address: '{}:{}'.format(address[0], address[1]), match))))
		if len(match) > 0:
			runMatch(match[0])


def runMatch(players):
	for i in range(len(players)):
		players[i] = clients[players[i]]

	state, next = Game(list(map(lambda P: P['name'], players)))
	state['current'] = 0

	print('{} VS {}'.format(players[0]['name'], players[1]['name']))

	attempts = 0
	try:
		while attempts < 3:
			print('Request move from {}'.format(players[state['current']]['name']))
			response = fetch(players[state['current']]['address'], {
				'request': 'play',
				'attempts': attempts,
				'state': state
			})
			if response['response'] == 'move':
				try:
					state = next(state, response['move'])
					attempts = 0
				except game.BadMove:
					print('Bad Move')
					attempts += 1
		print(players[state['current']]['name'], 'has done too many Bad Moves')
	except game.GameWin as e:
		print('Winner', players[e.winner])
	except game.GameDraw:
		print('Draw')

def processRequest(client, address):
	print('request from', address)
	try:
		data = receiveJSON(client)
		
		if data['request'] != 'subscribe':
			raise ValueError('Unknown request \'{}\''.format(data['request']))

		clientAddress = (address[0], int(data['port']))
	
		print('Subscription received for {} with address {}'.format(data['name'], clientAddress))
		
		sendJSON(client, {
			'response': 'ok'
		})

		Timer(2, subscribe, [clientAddress, data['name']]).start()

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

listenThread = Thread(target=processClients)
listenThread.start()


try:
	print('Ctrl-C to stop')
	while True:
		time.sleep(1)
except KeyboardInterrupt:
	print('bye')

running = False
listenThread.join()
