class GameWin(Exception):
	def __init__(self, winner, lastState):
		self.__winner = winner
		self.__state = lastState

	@property
	def winner(self):
		return self.__winner

	@property
	def state(self):
		return self.__state

	def __str__(self):
		return '{} win the game'.format(self.winner)

class BadMove(Exception):
	pass

class GameDraw(Exception):
	pass

class BadGameInit(Exception):
	pass
