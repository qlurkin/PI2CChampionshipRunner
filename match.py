import copy
from games.game import GameWin, GameDraw, BadMove

def tupleSet(T, index, value):
	L = list(T)
	L[index] = value
	return tuple(L)

class Match:
	def __init__(self, players):
		self.__players = tuple(players)
		self.__badMoves = (0,)*len(players)
		self.__state = None
		self.__moves = ()
		self.__status = 'waiting'
		self.__turn = 0
		self.__winner = None

	@property
	def players(self):
		return self.__players

	@property
	def badMoves(self):
		return self.__badMoves

	@property
	def state(self):
		return copy.deepcopy(self.__state)

	@property
	def moves(self):
		return copy.deepcopy(self.__moves)
	
	@property
	def status(self):
		return self.__status

	def incBadMove(self, turn):
		res = copy.copy(self)
		res.__badMoves = tupleSet(res.__badMoves, turn, res.__badMoves[turn]+1)
		res.__players = tupleSet(res.__players, turn, res.__players[turn].addBadMoves(1))
		return res

	def win(self, turn):
		res = copy.copy(self)
		L = []
		for i, player in self.__players:
			if i == turn:
				L.append(player.win())
			else:
				L.append(player.loose())
		res.__players = tuple(L)
		res.__status = 'finished'
		res.__winner = turn
		return res

	def draw(self):
		res = copy.copy(self)
		L = []
		for i, player in self.__players:
			L.append(player.draw())
		res.__players = tuple(L)
		res.__status = 'finished'
		return res

	def updateState(self, fun, move):
		res = copy.copy(self)
		try:
			res.__status = 'playing'
			res.__moves += (move,)
			res.__state = fun(self.state, move)
		except GameWin as e:
			res.__state = e.state
			res = res.win(e.winner)
		except GameDraw as e:
			res.__state = e.state
			res = res.draw()
		except BadMove as e:
			res = res.incBadMove(res.__turn)
			
		return res

	