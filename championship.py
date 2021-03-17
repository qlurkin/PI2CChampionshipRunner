import copy
from match import Match

class __Championship:
	def __init__(self):
		self.__players = ()
		self.__matches = ()
		self.__current = 0

	@property
	def players(self):
		return self.__players

	@property
	def matches(self):
		return self.__matches

	@property
	def currentMatch(self):
		if self.__current < len(self.__matches):
			return self.__matches[self.__current]
		return None

	def nextMatch(self):
		current = self.currentMatch
		if current is not None:
			if current.status == 'finished':
				res = copy.copy(self)
				res.__current += 1
				return res
		return self

	def setCurrentMatch(self, value):
		if self.__current < len(self.__matches):
			matches = list(self.__matches)
			matches[self.__current] = value
			res = copy.copy(self)
			res.__matches = tuple(matches)
			return res
		return self

	def addPlayer(self, player):
		res = copy.copy(self)
		for opponent in self.__players:
			res.__matches = res.__matches + (Match((player, opponent)),)
			res.__matches = res.__matches + (Match((opponent, player)),)
		res.__players = res.__players + (player,)

		return res

	def __str__(self):
		return "Championship"

__TheChampionship = __Championship()

def getChampionship():
	return __TheChampionship

def updateChampionship(fun):
	__TheChampionship = fun(__TheChampionship)

# def State(state):
# 	def setState(fun):
# 		nonlocal state
# 		state = fun(state)

# 	def getState():
# 		return copy.copy(state)

# 	return getState, setState

# getState, setState = State({
# 	"clients": [],
# 	"matches": []
# })

# def dictSet(D, key, value):
# 	res = dict(D)
# 	res[key] = value
# 	return res

# def listAppend(L, value):
# 	res = list(L)
# 	res.append(value)
# 	return res

# def addClient(client, state):
# 	return dictSet(state,
# 		"clients",
# 		listAppend(state["clients"], client)
# 	)

# def addMatch(match, state):
# 	return dictSet(state,
# 		"matches",
# 		listAppend(state["matches"], match)
# 	)
