import copy

def Datastore(initial):
	state = copy.copy(initial)

	def getState():
		return copy.copy(state)

	def setState(value):
		nonlocal state
		state = value

	def updateState(fun):
		setState(fun(state))

	return getState, setState, updateState

	