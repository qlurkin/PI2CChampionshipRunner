import copy
from immutable import List
from threading import Lock



def Datastore(initial):
	state = copy.copy(initial)
	observers = List()
	stateLock = Lock()

	def getState():
		return copy.copy(state)

	def updateState(fun):
		nonlocal state
		with stateLock:
			state = fun(state)
		for callback in observers:
			callback(state)

	def subscribe(callback):
		nonlocal observers
		observers = observers.append(callback)
		return callback

	return getState, updateState, subscribe

	