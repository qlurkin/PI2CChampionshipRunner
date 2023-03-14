from .. import game
import copy
import random
from collections import deque

#       A     B     C
#    0  1  2  3  4  5  6
# L  7  8  9 10 11 12 13 D
#   14 15 16 17 18 19 20
# K 21 22 23 24 25 26 27 E
#   28 29 30 31 32 33 34
# J 35 36 37 38 39 40 41 F
#   42 43 44 45 46 47 48
#       I     H     G
GATES = {
    "A": {"start": 1, "end": 43, "inc": 7},
    "B": {"start": 3, "end": 45, "inc": 7},
    "C": {"start": 5, "end": 47, "inc": 7},
    "D": {"start": 13, "end": 7, "inc": -1},
    "E": {"start": 27, "end": 21, "inc": -1},
    "F": {"start": 41, "end": 35, "inc": -1},
    "G": {"start": 47, "end": 5, "inc": -7},
    "H": {"start": 45, "end": 3, "inc": -7},
    "I": {"start": 43, "end": 1, "inc": -7},
    "J": {"start": 35, "end": 41, "inc": 1},
    "K": {"start": 21, "end": 27, "inc": 1},
    "L": {"start": 7, "end": 13, "inc": 1},
}

DIRECTIONS = {
    "N": {"coords": (-1, 0), "inc": -7, "opposite": "S"},
    "S": {"coords": (1, 0), "inc": 7, "opposite": "N"},
    "W": {"coords": (0, -1), "inc": -1, "opposite": "E"},
    "E": {"coords": (0, 1), "inc": 1, "opposite": "W"},
    (-1, 0): {"name": "N"},
    (1, 0): {"name": "S"},
    (0, -1): {"name": "W"},
    (0, 1): {"name": "E"},
}


def slideTiles(board, free, gate):
    start = GATES[gate]["start"]
    end = GATES[gate]["end"]
    inc = GATES[gate]["inc"]

    new_free = board[end]
    new_board = copy.deepcopy(board)
    dest = end
    src = end - inc
    while dest != start:
        new_board[dest] = new_board[src]
        dest = src
        src -= inc
    new_board[start] = free
    return new_board, new_free


def onTrack(index, gate):
    return index in range(
        GATES[gate]["start"],
        GATES[gate]["end"] + GATES[gate]["inc"],
        GATES[gate]["inc"],
    )


def turn_tile(tile):
    res = copy.deepcopy(tile)
    res["N"] = tile["E"]
    res["E"] = tile["S"]
    res["S"] = tile["W"]
    res["W"] = tile["N"]
    return res


def isSameTile(t1, t2):
    for _ in range(4):
        if t1 == t2:
            return True
        t2 = turn_tile(t2)

    return False


def random_turn_tile(tile):
    for _ in range(random.randint(1, 4)):
        tile = turn_tile(tile)
    return tile


def makeTiles():
    tiles = []
    straight = {"N": True, "E": False, "S": True, "W": False, "item": None}
    corner = {"N": True, "E": True, "S": False, "W": False, "item": None}
    tee = {"N": True, "E": True, "S": True, "W": False, "item": None}
    for _ in range(12):
        tiles.append(random_turn_tile(straight))
    for _ in range(10):
        tiles.append(random_turn_tile(corner))
    treasure = 12
    for _ in range(6):
        tiles.append(random_turn_tile(dict(corner, item=treasure)))
        treasure += 1
    for _ in range(6):
        tiles.append(random_turn_tile(dict(tee, item=treasure)))
        treasure += 1
    random.shuffle(tiles)
    return tiles


def index2coords(index):
    return index // 7, index % 7


def coords2index(i, j):
    return i * 7 + j


def isCoordsValid(i, j):
    return i >= 0 and i < 7 and j >= 0 and i < 7


def add(A, B):
    return tuple(a + b for a, b in zip(A, B))


def BFS(start, successors, goals):
    q = deque()
    parent = {}
    parent[start] = None
    node = start
    while node not in goals:
        for successor in successors(node):
            if successor not in parent:
                parent[successor] = node
                q.append(successor)
        node = q.popleft()

    res = []
    while node is not None:
        res.append(node)
        node = parent[node]

    return list(reversed(res))


def path(start, end, board):
    def successors(index):
        res = []
        for dir in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            coords = add(index2coords(index), dir)
            dirName = DIRECTIONS[dir]["name"]
            opposite = DIRECTIONS[dirName]["opposite"]
            # breakpoint()
            if isCoordsValid(*coords):
                if board[index][dirName] and board[coords2index(*coords)][opposite]:
                    res.append(coords2index(*coords))
        return res

    try:
        res = BFS(start, successors, [end])
        print(res)
        return res
    except IndexError:
        return None


def Labyrinthe(players):
    if len(players) != 2:
        raise game.BadGameInit("We only support 2 players Game")

    # 12 droit
    # 10 90°
    # 6 90° avec trésor
    # 6 tri avec trésor
    #
    # 12 trésor sur les fixes

    board: list[dict | None] = [None] * 49
    board[0] = {"N": False, "E": True, "S": True, "W": False, "item": None}
    board[2] = {"N": False, "E": True, "S": True, "W": True, "item": 0}
    board[4] = {"N": False, "E": True, "S": True, "W": True, "item": 1}
    board[6] = {"N": False, "E": False, "S": True, "W": True, "item": None}
    board[14] = {"N": True, "E": True, "S": True, "W": False, "item": 2}
    board[16] = {"N": True, "E": True, "S": True, "W": False, "item": 3}
    board[18] = {"N": False, "E": True, "S": True, "W": True, "item": 4}
    board[20] = {"N": True, "E": False, "S": True, "W": True, "item": 5}
    board[28] = {"N": True, "E": True, "S": True, "W": False, "item": 6}
    board[30] = {"N": True, "E": True, "S": False, "W": True, "item": 7}
    board[32] = {"N": True, "E": False, "S": True, "W": True, "item": 8}
    board[34] = {"N": True, "E": False, "S": True, "W": True, "item": 9}
    board[42] = {"N": True, "E": True, "S": False, "W": False, "item": None}
    board[44] = {"N": True, "E": True, "S": False, "W": True, "item": 10}
    board[46] = {"N": True, "E": True, "S": False, "W": True, "item": 11}
    board[48] = {"N": True, "E": False, "S": False, "W": True, "item": None}

    tiles = makeTiles()
    for i, tile in enumerate(board):
        if tile is None:
            board[i] = tiles.pop()

    free = tiles.pop()

    treasures = list(range(24))
    random.shuffle(treasures)

    targets = [[], []]

    for _ in range(4):
        targets[0].append(treasures.pop())
        targets[1].append(treasures.pop())

    state = {
        "players": players,
        "current": 0,
        "positions": [0, 48],
        "board": board,
        "tile": free,
        "target": targets[0][-1],
        "remaining": len(targets[0]),
    }

    def next(state, move):
        if move is None:
            raise game.BadMove("None is not a valid Move")

        try:
            if not isSameTile(state["tile"], move["tile"]):
                raise game.BadMove(
                    "The free tile in the move is not the free tile of the state"
                )
            if move["gate"] not in "ABCDEFGHIJKL":
                raise game.BadMove("Invalid gate")
            if move["new_position"] not in range(49):
                raise game.BadMove("Invalid new position")
        except KeyError as e:
            raise game.BadMove("Missing key {}".format(e))

        new_state = copy.deepcopy(state)

        new_board, new_free = slideTiles(state["board"], move["tile"], move["gate"])
        new_state["board"] = new_board
        new_state["tile"] = new_free

        new_positions = []
        for position in state["positions"]:
            if onTrack(position, move["gate"]):
                if position == GATES[move["gate"]]["end"]:
                    new_positions.append(GATES[move["gate"]]["start"])
                    continue
                new_positions.append(position + GATES[move["gate"]]["inc"])
                continue
            new_positions.append(position)

        new_state["positions"] = new_positions

        if (
            path(
                new_state["positions"][state["current"]],
                move["new_position"],
                new_state["board"],
            )
            is None
        ):
            raise game.BadMove("Your new_position is unreachable")

        new_state["positions"][state["current"]] = move["new_position"]

        if (
            new_state["board"][new_state["positions"][state["current"]]]["item"]
            == targets[state["current"]][-1]
        ):
            targets[state["current"]].pop()
            if len(targets[state["current"]]) == 0:
                new_state["remaining"] = 0
                new_state["target"] = None
                raise game.GameWin(state["current"], new_state)

        new_state["current"] = (new_state["current"] + 1) % 2

        new_state["target"] = targets[new_state["current"]][-1]
        new_state["remaining"] = len(targets[new_state["current"]])

        return new_state

    return state, next


def showBoard(board):
    mat = []
    for i in range(28):
        mat.append([])
        for j in range(28):
            mat[i].append(" ")
    for index, value in enumerate(board):
        i = (index // 7) * 4
        j = (index % 7) * 4
        mat[i][j] = "#"
        mat[i][j + 1] = "#" if not value["N"] else " "
        mat[i][j + 2] = "#"
        mat[i][j + 3] = "|"
        mat[i + 1][j] = "#" if not value["W"] else " "
        mat[i + 1][j + 1] = (
            " " if value["item"] is None else chr(ord("A") + value["item"])
        )
        mat[i + 1][j + 2] = "#" if not value["E"] else " "
        mat[i + 1][j + 3] = "|"
        mat[i + 2][j] = "#"
        mat[i + 2][j + 1] = "#" if not value["S"] else " "
        mat[i + 2][j + 2] = "#"
        mat[i + 2][j + 3] = "|"
        mat[i + 3][j] = "-"
        mat[i + 3][j + 1] = "-"
        mat[i + 3][j + 2] = "-"
        mat[i + 3][j + 3] = "-"

    print("\n".join(["".join(line) for line in mat]))


def showState(state):
    print("Player:", state["players"][state["current"]])
    print("Target:", state["target"])
    print("Remaining:", state["remaining"])
    print("Tile:", state["tile"])
    print("Positions:")
    for i, pos in enumerate(state["positions"]):
        print(" - {}: {}".format(state["players"][i], pos))
    showBoard(state["board"])


Game = Labyrinthe

if __name__ == "__main__":
    state, next = Game(["LUR", "HSL"])
    state = {
        "players": ["LUR", "HSL"],
        "current": 0,
        "positions": [0, 48],
        "board": [
            {"N": False, "E": True, "S": True, "W": False, "item": None},
            {"N": False, "E": True, "S": False, "W": True, "item": None},
            {"N": False, "E": True, "S": True, "W": True, "item": 0},
            {"N": False, "E": True, "S": True, "W": False, "item": 14},
            {"N": False, "E": True, "S": True, "W": True, "item": 1},
            {"N": True, "E": False, "S": False, "W": True, "item": None},
            {"N": False, "E": False, "S": True, "W": True, "item": None},
            {"N": False, "E": False, "S": True, "W": True, "item": 15},
            {"N": False, "E": True, "S": False, "W": True, "item": None},
            {"N": True, "E": False, "S": False, "W": True, "item": None},
            {"N": True, "E": False, "S": True, "W": False, "item": None},
            {"N": True, "E": False, "S": True, "W": False, "item": None},
            {"N": True, "E": False, "S": True, "W": False, "item": None},
            {"N": False, "E": True, "S": False, "W": True, "item": None},
            {"N": True, "E": True, "S": True, "W": False, "item": 2},
            {"N": False, "E": True, "S": False, "W": True, "item": None},
            {"N": True, "E": True, "S": True, "W": False, "item": 3},
            {"N": False, "E": False, "S": True, "W": True, "item": None},
            {"N": False, "E": True, "S": True, "W": True, "item": 4},
            {"N": False, "E": True, "S": True, "W": True, "item": 23},
            {"N": True, "E": False, "S": True, "W": True, "item": 5},
            {"N": False, "E": True, "S": False, "W": True, "item": None},
            {"N": False, "E": True, "S": True, "W": True, "item": 22},
            {"N": False, "E": True, "S": False, "W": True, "item": None},
            {"N": True, "E": False, "S": True, "W": True, "item": 19},
            {"N": True, "E": False, "S": True, "W": False, "item": None},
            {"N": True, "E": False, "S": False, "W": True, "item": 17},
            {"N": True, "E": False, "S": False, "W": True, "item": None},
            {"N": True, "E": True, "S": True, "W": False, "item": 6},
            {"N": True, "E": True, "S": False, "W": False, "item": 16},
            {"N": True, "E": True, "S": False, "W": True, "item": 7},
            {"N": True, "E": True, "S": False, "W": False, "item": 12},
            {"N": True, "E": False, "S": True, "W": True, "item": 8},
            {"N": True, "E": False, "S": False, "W": True, "item": None},
            {"N": True, "E": False, "S": True, "W": True, "item": 9},
            {"N": True, "E": False, "S": False, "W": True, "item": None},
            {"N": True, "E": True, "S": True, "W": False, "item": 21},
            {"N": True, "E": False, "S": True, "W": False, "item": None},
            {"N": True, "E": True, "S": False, "W": False, "item": None},
            {"N": True, "E": False, "S": False, "W": True, "item": None},
            {"N": False, "E": False, "S": True, "W": True, "item": None},
            {"N": True, "E": True, "S": False, "W": True, "item": 20},
            {"N": True, "E": True, "S": False, "W": False, "item": None},
            {"N": False, "E": True, "S": True, "W": False, "item": None},
            {"N": True, "E": True, "S": False, "W": True, "item": 10},
            {"N": False, "E": True, "S": True, "W": False, "item": 13},
            {"N": True, "E": True, "S": False, "W": True, "item": 11},
            {"N": True, "E": False, "S": True, "W": False, "item": None},
            {"N": True, "E": False, "S": False, "W": True, "item": None},
        ],
        "tile": {"N": True, "E": True, "S": True, "W": False, "item": 18},
        "target": 7,
        "remaining": 4,
    }
    showState(state)
    state = next(state, {"tile": state["tile"], "gate": "C", "new_position": 8})
    showState(state)
