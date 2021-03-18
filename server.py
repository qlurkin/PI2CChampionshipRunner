import socket
from jsonNetwork import sendJSON, receiveJSON, NotAJSONObject, fetch
from threading import Thread, Timer
import importlib
import sys
from championship import Championship, addPlayer, getAllPlayers, getState, changePlayerStatus, updateState, hookRegister
from graphics import ui

def checkClient(address):
	'''
		Ping client
	'''
	print('checking client {}:'.format(address), end=' ')
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
	for client in getAllPlayers(getState()):
		status = checkClient(client['address'])
		updateState(changePlayerStatus(client['address'], status))


def finalizeSubscription(address, name, matricules):
	'''
		Add client if successfully pinged
	'''
	status = checkClient(address)
	if status == 'online':
		updateState(addPlayer(name, address, matricules))


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

def formatClient(client):
	return '{}: {}'.format(client['name'], client['points'])

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

	hookRegister('matchEnd', checkAllClient)

	stopChampionship = Championship(Game)

	ui(gameName, render)

	stopSubscriptions()
	stopChampionship()
