class GameWin(Exception):
	def __init__(self, winner):
		self.__winner = winner

	@property
	def winner(self):
		return self.__winner

	def __str__(self):
		return '{} win the game'.format(self.winner)

class BadMove(Exception):
	pass

class BadGameInit(Exception):
	pass
