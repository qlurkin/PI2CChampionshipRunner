import copy

__chats = []

def getChats():
	return copy.deepcopy(__chats)

def postChat(name, message):
	__chats.append({
		"name": name,
		"message": message
	})

	if name == 'Admin':
		print(message)

	if len(__chats) > 20:
		del(__chats[0])