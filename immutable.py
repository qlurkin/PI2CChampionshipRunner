class List:
	def __init__(self, iterable=[]):
		self.__items = tuple(iterable)

	def append(self, item):
		return List(self.__items + (item,))

	def __getitem__(self, index):
		if isinstance(index, slice):
			return List(self.__items[index])
		return self.__items[index]

	def __len__(self):
		return len(self.__items)

	def set(self, index, value):
		return List(self.__items[:index] + (value,) + self.__items[index+1:])

	def update(self, index, fun):
		return self.set(index, fun(self[index]))

	def __str__(self):
		return 'List' + str(self.__items)

	def __add__(self, other):
		return List(self.__items + other.__items)

	def __contains__(self, item):
		return item in self.__items

	def index(self, item):
		return self.__items.index(item)

	def __copy__(self):
		return self

	def remove(self, index):
		return List(self.__items[:index] + self.__items[index+1:])

	def pop(self, index=-1):
		elem = self[index]
		return self.remove(index), elem


class Map:
	def __init__(self, *args, **kwargs):
		self.__map = dict(*args, **kwargs)

	def __getitem__(self, key):
		return self.__map[key]

	def __len__(self):
		return len(self.__map)

	def __iter__(self):
		return iter(self.__map)

	def items(self):
		return self.__map.items()

	def values(self):
		return self.__map.values()

	def keys(self):
		return self.__map.keys()

	def set(self, key, value):
		map = dict(self.__map)
		map[key] = value
		return Map(map)

	def update(self, key, fun):
		return self.set(key, fun(self[key]))

	def __str__(self):
		return 'Map' + str(self.__map)

	def __contains__(self, key):
		return key in self.__map

	def __copy__(self):
		return self

	def remove(self, key):
		map = dict(self.__map)
		del(map[key])
		return Map(map)

	def pop(self, key):
		value = self[key]
		return self.remove(key), value

if __name__ == '__main__':
	print(dir(list()))
	L = List()
	L = L.append(5).append(6)
	print(L)
	print(L[1:])

	print(5 in L)

	#L[0] = 8

	for elem in L:
		print(elem)

	print(len(L))

	M = Map()
	M = M.set('truc', 42).set('machin', 3.14)
	print(M)
	print(M['truc'])

	print('truc' in M)

	for k in M:
		print(k)

def append(item):
	def fun(L: List):
		return L.append(item)
	return fun

def setValue(keyOrIndex, value):
	def fun(ListOrMap):
		return ListOrMap.set(keyOrIndex, value)
	return fun

def remove(keyOrIndex):
	def fun(ListOrMap):
		return ListOrMap.remove(keyOrIndex)
	return fun