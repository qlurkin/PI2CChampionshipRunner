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

	def __str__(self):
		return 'List' + str(self.__items)

	def __add__(self, other):
		return List(self.__items + other.__items)

	def __contains__(self, item):
		return item in self.__items

	def index(self, item):
		return self.__items.index(item)

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

	def __str__(self):
		return 'Map' + str(self.__map)

	def __contains__(self, key):
		return key in self.__map

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
