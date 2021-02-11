import game
import copy

def same(L):
	if L[0] == None:
		return False
	for elem in L:
		if elem != L[0]:
			return False
	return True

def getLine(board, i):
	return board[i*3:(i+1)*3]

def getColumn(board, j):
	return [board[i] for i in range(j, 9, 3)]

# dir == 1 or -1
def getDiagonal(board, dir):
	start = 0 if dir == 1 else 2
	return [board[start + i*(3+dir)] for i in range(3)]

def isWinning(board):
	for i in range(3):
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

def TicTacToe(players):
	if len(players) != 2:
		raise game.BadGameInit('Tic Tac Toe must be played by 2 players')

	symbols = ['X', 'O']

	state = {
		'players': players,
		'current': 0,
		'board': [None] * 9
	}

	def next(state, move):
		newState = copy.deepcopy(state)
		
		try:
			move = int(move)
			state['board'][move]
		except:
			raise game.BadMove('Move must be an integer between 0 and 8 inclusive')

		if state['board'][move] is not None:
			raise game.BadMove('These place is not free')

		newState['board'][move] = symbols[state['current']]

		if isWinning(newState['board']):
			raise game.GameWin(state['current'], newState)

		if isFull(newState['board']):
			raise game.GameDraw()

		newState['current'] = (state['current'] + 1) % 2
		return newState

	return state, next

Game = TicTacToe

if __name__=='__main__':
	def show(board):
		for i in range(3):
			print(getLine(board, i))

	state, next = TicTacToe(['LUR', 'LRG'])
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
