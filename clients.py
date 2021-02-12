from threading import Lock
import copy
import json

__clients = {}
__match = []
__matchLock = Lock()

def add(address, name, matricules):
	with __matchLock:
		if address not in __clients:
			for opponent in __clients:
				__match.append([address, opponent])
				__match.append([opponent, address])

			__clients[address] = {
				'address': address,
				'points': 0,
				'badMoves': 0,
				'matchCount': 0,
				'matricules': matricules
			}

		__clients[address]['name'] = name
		__clients[address]['status'] = 'online'

def getMatch():
	players = None
	with __matchLock:
		if len(__match) > 0:
			players = __match[0]
			__match[0:1] = []
	return players

def get(address):
	return copy.deepcopy(__clients[address])

def matchWin(players, winner):
	for player in players:
		__clients[player]['matchCount'] += 1
	__clients[players[winner]]['points'] += 3

def matchDraw(players):
	for player in players:
		__clients[player]['points'] += 1
		__clients[player]['matchCount'] += 1

def addBadMoves(player, count):
	__clients[player]['badMoves'] += count

def save():
	with open('data.json', 'w', encoding='utf8') as file:
		json.dump(list(__clients.values()), file, indent='\t')


