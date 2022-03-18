from datastore import Datastore
from immutable import List, Map, append, remove

getChats, updateChats, subscribe = Datastore(List())

def postChat(name, message):
	updateChats(append(Map({
		"name": name,
		"message": message
	})))

	if name == 'Admin':
		print(message)

	if len(getChats()) > 20:
		updateChats(remove(0))