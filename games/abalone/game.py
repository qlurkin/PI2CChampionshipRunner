from games import game
import copy

directions = {
	'NE': ( 0, -1),
	'SW': ( 0,  1),
	'NW': (-1, -1),
	'SE': ( 1,  1),
	 'E': ( 1,  0),
	 'W': (-1,  0)
}

opposite = {
	'NE': 'SW',
	'SW': 'NE',
	'NW': 'SE',
	'SE': 'NW',
	'E': 'W',
	'W': 'E'
}

def areAligned(marbles):
	marbles = sorted(marbles, key=lambda L: L[0]*9+L[1])
	D = set()
	for i in range(len(marbles)-1):
		direction = (marbles[i+1][0]-marbles[i][0], marbles[i+1][1]-marbles[i][1])
		if direction not in directions.values():
			return False
		D.add(direction)
	return len(D) < 2, D[0].pop() if len(D) == 1 else None

def validate(move):
	marbles = move['marbles']
	if not 0 < len(marbles) < 4:
		raise game.BadMove('You can only move 1, 2, or 3 marbles')
	
	aligned, marblesDir = areAligned(marbles)
	if not aligned:
		raise game.BadMove('The marbles you want to move must be aligned')

	if len(marbles) == 1:
		

def extendBoard(board):
	eBoard = []
	eBoard.append(['X']*11)
	for line in board:
		eBoard.append(['X'] + line + ['X'])
	eBoard.append(['X']*11)

	return eBoard

def normalBoard(eBoard):
	board = []
	for i in range(1, 10):
		board.append(eBoard[i][1:10])
	return board

def Abalone(players):
	if len(players) != 2:
		raise game.BadGameInit('Tic Tac Toe must be played by 2 players')

	symbols = ['B', 'W']

	state = {
		'players': players,
		'current': 0,
		'board': [
			['W', 'W', 'W', 'W', 'W', 'X', 'X', 'X', 'X'],
			['W', 'W', 'W', 'W', 'W', 'W', 'X', 'X', 'X'],
			['E', 'E', 'W', 'W', 'W', 'E', 'E', 'X', 'X'],
			['E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'X'],
			['E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E'],
			['X', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E'],
			['X', 'X', 'E', 'E', 'B', 'B', 'B', 'E', 'E'],
			['X', 'X', 'X', 'B', 'B', 'B', 'B', 'B', 'B'],
			['X', 'X', 'X', 'X', 'B', 'B', 'B', 'B', 'B']
		]
	}

	# move = {
	# 	'marbles': [],
	# 	'direction': ''
	# }

	def next(state, move):
		pass

	return state, next

Game = Abalone

if __name__=='__main__':
	pass