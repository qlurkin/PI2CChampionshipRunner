import socket
from jsonNetwork import sendJSON, receiveJSON, NotAJSONObject
from threading import Thread
import time

inscriptionSocket = socket.socket()
inscriptionSocket.bind(('0.0.0.0', 3000))
inscriptionSocket.settimeout(1)
inscriptionSocket.listen()

running = True

players = {}

def processRequest(client, address):
	print('request from', address)
	try:
		data = receiveJSON(client)
		
		if data['request'] != 'subscribe':
			raise ValueError('Unknown request \'{}\''.format(data['request']))

		clientAddress = (address[0], int(data['port']))
		
		players[clientAddress] = {
			'name': data['name'],
			'address': clientAddress
		}
		
		print('{} subscribed with address {}'.format(players[clientAddress]['name'], players[clientAddress]['address']))
		
		sendJSON(client, {
			'response': 'ok'
		})
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
