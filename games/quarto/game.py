if __name__ == "__main__":
    import os
    import sys

    sys.path.append(os.getcwd())

from games import game
import copy


def same(L):
    if None in L:
        return False
    common = frozenset(L[0])
    for elem in L[1:]:
        common = common & frozenset(elem)
    return len(common) > 0


def getLine(board, i):
    return board[i * 4 : (i + 1) * 4]


def getColumn(board, j):
    return [board[i] for i in range(j, 16, 4)]


# dir == 1 or -1
def getDiagonal(board, dir):
    start = 0 if dir == 1 else 3
    return [board[start + i * (4 + dir)] for i in range(4)]


def isWinning(board):
    for i in range(4):
        if same(getLine(board, i)):
            return True
        if same(getColumn(board, i)):
            return True
    if same(getDiagonal(board, 1)):
        return True
    return same(getDiagonal(board, -1))


def isFull(board):
    for elem in board:
        if elem is None:
            return False
    return True


def Quarto(players):
    if len(players) != 2:
        raise game.BadGameInit("Tic Tac Toe must be played by 2 players")

    # Big/Small: B/S
    # Dark/Light: D/L
    # Empty/Full: E/F
    # Cylinder/Prism: C/P
    pieces = set()
    for size in ["B", "S"]:
        for color in ["D", "L"]:
            for weight in ["E", "F"]:
                for shape in ["C", "P"]:
                    pieces.add(frozenset({size, color, weight, shape}))

    state = {"players": players, "current": 0, "board": [None] * 16, "piece": None}

    # Move
    # {
    #   "pos": <index>,        # between 0 and 15 or null if first move
    #   "piece": <piece_str>,  # piece for the opponent example "BDEC"
    # }

    def next(state, move):
        newState = copy.deepcopy(state)

        if state["piece"] is not None:
            if "pos" not in move:
                raise game.BadMove("Move must contains a 'pos' key")

            try:
                pos = int(move["pos"])
                state["board"][pos]
            except (ValueError, IndexError):
                raise game.BadMove(
                    "Move['pos'] must be an integer between 0 and 15 inclusive"
                )

            if state["board"][pos] is not None:
                raise game.BadMove(f"These place '{pos}' is not free")

            newState["board"][pos] = state["piece"]

            if isWinning(newState["board"]):
                raise game.GameWin(state["current"], newState)

            if isFull(newState["board"]):
                raise game.GameDraw(newState)

        if "piece" not in move:
            raise game.BadMove("Move must contains a 'piece' key")

        if not isinstance(move["piece"], str):
            raise game.BadMove("Move['piece'] must be a str")

        piece = frozenset(move["piece"])

        if piece not in pieces:
            print(pieces)
            raise game.BadMove(f"Piece '{move['piece']}' not available")

        newState["piece"] = move["piece"]

        newState["current"] = (state["current"] + 1) % 2
        pieces.remove(piece)
        return newState

    return state, next


Game = Quarto

if __name__ == "__main__":

    def show(board):
        for i in range(4):
            print(getLine(board, i))

    def input_move(player):
        print(f"player {player}")
        pos = input("Pos (enter for `null`): ")
        if len(pos) == 0:
            pos = None
        else:
            pos = int(pos)
        piece = input("Piece (enter for `null`): ")
        if len(piece) == 0:
            piece = None
        return {"pos": pos, "piece": piece}

    state, next = Quarto(["LUR", "FKY"])
    try:
        while True:
            show(state["board"])
            print(f"Piece: {state['piece']}")
            move = input_move(state["players"][state["current"]])
            try:
                state = next(state, move)
            except game.BadMove as e:
                print(e)
    except game.GameWin as e:
        show(e.state["board"])
        print("{} win the game".format(state["players"][e.winner]))
