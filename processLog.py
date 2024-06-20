import jsonpickle
import sys

stateFilename = sys.argv[1]


class Truc:
    def __call__(self, *args, **kwargs):
        print(args)
        print(kwargs)


with open(stateFilename, encoding="utf8") as file:
    data = jsonpickle.decode(file.read())
    for client in data.clients.values():
        print(
            list(client.matricules),
            client.name,
            "->",
            data.getBadMoves(client) / data.getMatchCount(client),
        )
