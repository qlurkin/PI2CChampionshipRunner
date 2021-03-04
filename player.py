import copy

class Player:
	'''Immutable Player'''

	def __init__(self, name, address, matricules):
		self.__name = name
		self.__address = tuple(address)
		self.__matricules = tuple(matricules)
		self.__points = 0
		self.__badMoves = 0
		self.__matchCount = 0
		self.__status = 'pending'

	@property
	def name(self):
		return self.__name

	@property
	def address(self):
		return self.__address

	@property
	def matricules(self):
		return self.__matricules

	@property
	def points(self):
		return self.__points

	@property
	def badMoves(self):
		return self.__badMoves

	@property
	def matchCount(self):
		return self.__matchCount

	@property
	def status(self):
		return self.__status

	def addBadMoves(self, count):
		res = copy.copy(self)
		res.__badMoves += count
		return res

	def win(self):
		res = copy.copy(self)
		res.__points += 3
		res.__matchCount += 1
		return res

	def loose(self):
		res = copy.copy(self)
		res.__matchCount += 1
		return res

	def draw(self):
		res = copy.copy(self)
		res.__points += 1
		res.__matchCount += 1
		return res

	def setStatus(self, status):
		res = copy.copy(self)
		res.__status = status
		return res

	def __str__(self):
		return '{} ({}:{}) {} - #: {}, points: {}, BM: {}, status: {}'.format(
			self.name,
			self.address[0],
			self.address[1],
			self.matricules,
			self.matchCount,
			self.points,
			self.badMoves,
			self.status
		)

if __name__ == '__main__':
	c = Player('Bot', ('localhost', 3000), ['LUR', 'LRG'])
	c2 = c.addBadMoves(3).win().loose().draw().setStatus('online')
	print(c)
	print(c2)
