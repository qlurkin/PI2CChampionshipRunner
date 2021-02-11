import socket
from jsonNetwork import sendJSON, receiveJSON, NotAJSONObject
from threading import Thread, Timer, Lock
import time

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
			clients[address]['status'] = 'online'
		else:
			raise ValueError()
	except:
		clients[address]['status'] = 'lost'
	print(clients[address]['status'])

def checkAllClients():
	for address in clients:
		checkClient(address)

def processRequest(client, address):
	print('request from', address)
	try:
		data = receiveJSON(client)
		
		if data['request'] != 'subscribe':
			raise ValueError('Unknown request \'{}\''.format(data['request']))

		clientAddress = (address[0], int(data['port']))
		
		with matchLock:

			for opponent in clients:
				match.append([clientAddress, opponent])
				match.append([opponent, clientAddress])
			
			clients[clientAddress] = {
				'name': data['name'],
				'address': clientAddress,
				'status': 'pending'
			}
	
		print('{} subscribed with address {}'.format(clients[clientAddress]['name'], clients[clientAddress]['address']))
		
		sendJSON(client, {
			'response': 'ok'
		})

		Timer(2, checkClient, [clientAddress]).start()

		print('MATCH LIST:\n{}'.format('\n'.join(map(lambda address: '{}:{}'.format(address[0], address[1]), match))))

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
