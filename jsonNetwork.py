import socket as s
import json
import time

class NotAJSONObject(Exception):
	pass

class Timeout(Exception):
	pass

def sendJSON(socket, obj):
	message = json.dumps(obj)
	if message[0] != '{':
		raise NotAJSONObject('sendJSON support only JSON Object Type')
	message = message.encode('utf8')
	total = 0
	while total < len(message):
		sent = socket.send(message[total:])
		total += sent

def receiveJSON(socket, timeout = 1):
	finished = False
	message = ''
	data = ''
	start = time.time()
	while not finished:
		message += socket.recv(4096).decode('utf8')
		if len(message) > 0 and message[0] != '{':
			raise NotAJSONObject('Received message is not a JSON Object')
		try:
			data = json.loads(message)
			finished = True
		except json.JSONDecodeError:
			if time.time() - start > timeout:
				raise Timeout()
	return data

def fetch(address, data, timeout=1):
	'''
		Request response from address. Data is included in the request
	'''
	socket = s.socket()
	socket.connect(address)
	sendJSON(socket, data)
	response = receiveJSON(socket, timeout)
	return response