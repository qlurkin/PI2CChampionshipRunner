from datastore import Datastore
from immutable import Map, List
import time

getMatch, updateMatch, subscribe = Datastore(None)

def postMatchState(matchState):
	updateMatch(lambda state: matchState)
	#time.sleep(1)
