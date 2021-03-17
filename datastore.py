import copy
from immutable import List

def Datastore(initial):
	state = copy.copy(initial)
	observers = List()

	def getState():
		return copy.copy(state)

	def setState(value):
		nonlocal state
		state = value
		for callback in observers:
			callback(state)

	def updateState(fun):
		setState(fun(state))

	def subscribe(callback):
		nonlocal observers
		observers = observers.append(callback)
		return callback

	return getState, setState, updateState, subscribe

	