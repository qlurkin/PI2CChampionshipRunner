import copy

def Datastore(initial):
	state = copy.copy(initiale)

	def getState():
		return copy.copy(state)

	def setState(value):
		state = copy.copy(value)

	return getState, setState

	