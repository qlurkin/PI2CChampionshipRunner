class GameEnd(Exception):
	def __init__(self, lastState):
		self.__state = lastState

	@property
	def state(self):
		return self.__state

	def __str__(self):
		return 'Game Over'

class GameWin(GameEnd):
	def __init__(self, winner, lastState):
		super().__init__(lastState)
		self.__winner = winner

	@property
	def winner(self):
		return self.__winner

	def __str__(self):
		return super().__str__() + ': {} win the game'.format(self.winner)

class BadMove(Exception):
	pass

class GameDraw(GameEnd):
	def __init__(self, lastState):
		super().__init__(lastState)

	def __str__(self):
		return super().__str__() + ': Draw'

class GameLoop(GameDraw):
	def __init__(self, lastState):
		super().__init__(lastState)

	def __str__(self):
		return super().__str__() + ': Stopped because of lopping behavior'

class BadGameInit(Exception):
	pass
