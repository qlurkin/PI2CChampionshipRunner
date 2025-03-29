# NOT FINISHED !!

from games import game
import copy

def same(L):
	if L[0] == None:
		return False
	for elem in L:
		if elem != L[0]:
			return False
	return True

def getLine(board, i):
	return board[i*4:(i+1)*4]

def getColumn(board, j):
	return [board[i] for i in range(j, 16, 4)]

# dir == 1 or -1
def getDiagonal(board, dir):
	start = 0 if dir == 1 else 2
	return [board[start + i*(4+dir)] for i in range(4)]

def isWinning(board):
	for i in range(4):
		if same(getLine(board, i)):
			return True
		if same(getColumn(board, i)):
			return True
	if same(getDiagonal(board, 1)):
		return True
	return same(getDiagonal(board, -1))

def isFull(board):
	for elem in board:
		if elem is None:
			return False
	return True

def Quarto(players):
	if len(players) != 2:
		raise game.BadGameInit('Tic Tac Toe must be played by 2 players')
	
	# Big/Small: B/S
	# Dark/Light: D/L
	# Empty/Full: E/F
	# Cylinder/Prism: C/P

	pieces = []
	for size in ['B', 'S']:
		for color in ['D', 'L']:
			for weight in ['E', 'F']:
				for shape in ['C', 'P']:
					pieces.append(f'{size}{color}{weight}{shape}')

	state = {
		'players': players,
		'current': 0,
		'board': [None] * 16
	}

	def next(state, move):
		newState = copy.deepcopy(state)
		
		try:
			move = int(move)
			state['board'][move]
		except:
			raise game.BadMove('Move must be an integer between 0 and 15 inclusive')

		if state['board'][move] is not None:
			raise game.BadMove('These place is not free')

		newState['board'][move] = pieces[state['current']]

		if isWinning(newState['board']):
			raise game.GameWin(state['current'], newState)

		if isFull(newState['board']):
			raise game.GameDraw(newState)

		newState['current'] = (state['current'] + 1) % 2
		return newState

	return state, next

Game = Quarto

if __name__=='__main__':
	def show(board):
		for i in range(4):
			print(getLine(board, i))

	state, next = Quarto(['LUR', 'FKY'])
	try:
		while True:
			show(state['board'])
			move = input('{} move: '.format(state['players'][state['current']]))
			try:
				state = next(state, move)
			except game.BadMove as e:
				print(e)
	except game.GameWin as e:
		show(e.state['board'])
		print('{} win the game'.format(state['players'][e.winner]))
