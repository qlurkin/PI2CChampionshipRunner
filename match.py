from datastore import Datastore
from immutable import Map, List
import time

getMatch, updateMatch, subscribe = Datastore(None)


def tic(delay):
	def decorator(fun):
		last = None
		def wait():
			nonlocal last
			if last is None:
				elapsed = float('inf')
			else:
				elapsed = time.time() - last
			if elapsed > delay:
				last = time.time()
			else:
				time.sleep(delay - elapsed)
				last = time.time()
			
		def wrapper(*args, **kwargs):
			nonlocal last
			wait()
			return fun(*args, **kwargs)
		return wrapper
	return decorator
		
	

@tic(0.5)
def postMatchState(matchState):
	updateMatch(lambda state: matchState)
