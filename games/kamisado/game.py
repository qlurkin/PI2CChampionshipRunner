if __name__ == "__main__":
    import os
    import sys

    sys.path.append(os.getcwd())

from games import game
import random
from pprint import pprint
import copy

BOARD = [
    ["orange", "blue", "purple", "pink", "yellow", "red", "green", "brown"],
    ["red", "orange", "pink", "green", "blue", "yellow", "brown", "purple"],
    ["green", "pink", "orange", "red", "purple", "brown", "yellow", "blue"],
    ["pink", "purple", "blue", "orange", "brown", "green", "red", "yellow"],
    ["yellow", "red", "green", "brown", "orange", "blue", "purple", "pink"],
    ["blue", "yellow", "brown", "purple", "red", "orange", "pink", "green"],
    ["purple", "brown", "yellow", "blue", "green", "pink", "orange", "red"],
    ["brown", "green", "red", "yellow", "pink", "purple", "blue", "orange"],
]

START_POSITIONS = [
    ["blue", "pink", "red", "orange", "brown", "purple", "yellow", "green"],  # 1
    ["blue", "pink", "red", "brown", "orange", "purple", "yellow", "green"],  # 2
    ["blue", "red", "pink", "orange", "brown", "yellow", "purple", "green"],  # 3
    ["yellow", "orange", "green", "purple", "red", "blue", "brown", "pink"],  # 4
    ["blue", "orange", "red", "pink", "yellow", "purple", "brown", "green"],  # 5
    ["yellow", "blue", "red", "orange", "brown", "purple", "green", "pink"],  # 6
    ["blue", "red", "pink", "brown", "orange", "yellow", "purple", "green"],  # 7
    ["yellow", "green", "orange", "purple", "red", "brown", "blue", "pink"],  # 8
    ["pink", "orange", "green", "purple", "red", "blue", "brown", "yellow"],  # 9
    ["yellow", "blue", "red", "brown", "orange", "purple", "green", "pink"],  # 10
    ["pink", "blue", "red", "orange", "brown", "purple", "green", "yellow"],  # 11
    ["blue", "pink", "orange", "red", "purple", "brown", "yellow", "green"],  # 12
    ["yellow", "blue", "orange", "purple", "red", "brown", "green", "pink"],  # 13
    ["yellow", "green", "purple", "orange", "brown", "red", "blue", "pink"],  # 14
    ["pink", "green", "purple", "orange", "brown", "red", "blue", "yellow"],  # 15
    ["green", "pink", "red", "orange", "brown", "purple", "yellow", "blue"],  # 16
    ["blue", "red", "orange", "pink", "yellow", "brown", "purple", "green"],  # 17
    ["pink", "green", "orange", "purple", "red", "brown", "blue", "yellow"],  # 18
    ["pink", "blue", "red", "brown", "orange", "purple", "green", "yellow"],  # 19
    ["yellow", "green", "purple", "brown", "orange", "red", "blue", "pink"],  # 20
    ["pink", "orange", "green", "red", "purple", "blue", "brown", "yellow"],  # 21
    ["green", "pink", "red", "brown", "orange", "purple", "yellow", "blue"],  # 22
    ["green", "red", "pink", "orange", "brown", "yellow", "purple", "blue"],  # 23
    ["green", "orange", "red", "pink", "yellow", "purple", "brown", "blue"],  # 24
    ["pink", "green", "purple", "brown", "orange", "red", "blue", "yellow"],  # 25
    ["red", "green", "pink", "orange", "brown", "yellow", "blue", "purple"],  # 26
    ["green", "red", "pink", "brown", "orange", "yellow", "purple", "blue"],  # 27
    ["pink", "blue", "orange", "red", "purple", "brown", "green", "yellow"],  # 28
    ["red", "blue", "pink", "orange", "brown", "yellow", "green", "purple"],  # 29
    ["green", "pink", "orange", "red", "purple", "brown", "yellow", "blue"],  # 30
    ["red", "green", "pink", "brown", "orange", "yellow", "blue", "purple"],  # 31
    ["red", "orange", "green", "pink", "yellow", "blue", "brown", "purple"],  # 32
    ["green", "red", "orange", "pink", "yellow", "brown", "purple", "blue"],  # 33
    ["red", "blue", "pink", "brown", "orange", "yellow", "green", "purple"],  # 34
    ["red", "green", "orange", "pink", "yellow", "brown", "blue", "purple"],  # 35
    ["red", "blue", "orange", "pink", "yellow", "brown", "green", "purple"],  # 36
]

KINDS = ["dark", "light"]

DIRECTION_POSITIVE = {"dark": False, "light": True}

END_ROW = {"dark": 0, "light": 7}

START_ROW = {"dark": 7, "light": 0}

TILE = 1
COLOR = 0
KIND = 1


def blocked(board, position):
    r, c = position
    if DIRECTION_POSITIVE[board[r][c][TILE][KIND]]:
        wall_row = r + 1
    else:
        wall_row = r - 1

    res = True
    for i in range(max(c - 1, 0), min(c + 2, 8)):
        if board[wall_row][i][TILE] is None:
            res = False
    return res


def find_tile(board, color, kind):
    for r in range(8):
        for c in range(8):
            if board[r][c][TILE] == [color, kind]:
                return r, c
    raise ValueError(f"Tile ({color}, {kind}) not found.")


def kamisado(players):
    if len(players) != 2:
        raise game.BadGameInit("Kamisado must be played by 2 players")

    board = [[[color, None] for color in row] for row in BOARD]

    tokens = sorted(random.sample(range(36), 2))

    for i in range(2):
        for cell, color in zip(board[START_ROW[KINDS[i]]], START_POSITIONS[tokens[i]]):
            cell[1] = [color, KINDS[i]]

    state = {
        "players": players,
        "current": 0,
        "color": None,
        "board": board,
    }

    def next(state, move):
        try:
            if len(move) != 2:
                raise game.BadMove("A move must contains 2 positions.")
        except TypeError:
            raise game.BadMove("Moves must have a `len`")

        for i in range(2):
            try:
                if len(move[i]) != 2:
                    raise game.BadMove("A position must contains 2 coordinates.")
            except TypeError:
                raise game.BadMove("Positions must have a `len`")

            for j in range(2):
                if not isinstance(move[i][j], int):
                    raise game.BadMove("A coordinate must be an integer.")

                if move[i][j] < 0 or move[i][j] > 7:
                    raise game.BadMove(
                        "A coordinate must be in the range [0, 7] inclusive."
                    )

        start, end = move

        start_row, start_col = start
        end_row, end_col = end

        board = state["board"]
        players = state["players"]
        current = state["current"]
        color = state["color"]

        if board[start_row][start_col][TILE] is None:
            raise game.BadMove("There is no tile at the start position.")

        if board[start_row][start_col][TILE][KIND] != KINDS[current]:
            raise game.BadMove(f"Tile ({start_row}, {start_col}) is not yours.")

        if color is not None and board[start_row][start_col][TILE][COLOR] != color:
            raise game.BadMove(f"You must move the {color} tile.")

        if start == end:
            if not blocked(board, start):
                raise game.BadMove("You must move if you can.")
            else:
                return {
                    "players": players,
                    "current": (current + 1) % 2,
                    "color": board[end_row][end_col][COLOR],
                    "board": copy.deepcopy(board),
                }

        if board[end_row][end_col][TILE] is not None:
            raise game.BadMove("End position is not empty.")

        progress = end_row - start_row
        if progress > 0 == DIRECTION_POSITIVE[KINDS[current]]:
            raise game.BadMove("Tiles cannot go backward.")

        if end_col != start_col:
            if abs(end_col - start_col) != abs(end_row - start_row):
                raise game.BadMove("Tiles must move ahead or diagonally.")

        dir = [end_row - start_row, end_col - start_col]
        dir = map(lambda v: 0.0 if v == 0 else v / abs(v), dir)
        dir = map(round, dir)
        dir = list(dir)

        dr, dc = dir

        p = [start_row + dr, start_col + dc]
        ok = True
        while p != end:
            r, c = p
            if board[r][c][TILE] is not None:
                ok = False
            p = [r + dr, c + dc]

        if not ok:
            raise game.BadMove("Yon can't go through other tiles.")

        new_board = copy.deepcopy(board)
        new_board[end_row][end_col][TILE] = new_board[start_row][start_col][TILE]
        new_board[start_row][start_col][TILE] = None

        if end_row == END_ROW[KINDS[current]]:
            raise game.GameWin(
                current,
                {
                    "players": players,
                    "current": current,
                    "color": color,
                    "board": new_board,
                },
                f"{players[current]} wins",
            )

        other = (current + 1) % 2
        next_color = new_board[end_row][end_col][COLOR]
        next_tile = find_tile(new_board, next_color, KINDS[other])

        blocked_tiles = set()
        next_player = other
        while blocked(new_board, next_tile):
            if next_tile in blocked_tiles:
                raise game.GameWin(
                    other,
                    {
                        "players": players,
                        "current": other,
                        "color": next_color,
                        "board": new_board,
                    },
                    f"Deadlock !! {players[other]} wins",
                )
            blocked_tiles.add(next_tile)
            nr, nc = next_tile
            next_player = (next_player + 1) % 2
            next_tile = find_tile(
                new_board, new_board[nr][nc][COLOR], KINDS[next_player]
            )

        return {
            "players": players,
            "current": other,
            "color": next_color,
            "board": new_board,
        }

    return state, next


Game = kamisado

if __name__ == "__main__":
    colors = sorted(
        ["orange", "blue", "purple", "pink", "yellow", "red", "green", "brown"]
    )
    for i, line in enumerate(START_POSITIONS):
        if sorted(line) != colors:
            print(f"Error in START_POSITIONS[{i}]")
    for i, line in enumerate(BOARD):
        if sorted(line) != colors:
            print(f"Error in BOARD[{i}]")

    state, next = Game(["LUR", "FKY"])
    pprint(state)

    state["board"] = [
        [
            ["orange", ["green", "light"]],
            ["blue", ["pink", "light"]],
            ["purple", ["red", "light"]],
            ["pink", ["orange", "light"]],
            ["yellow", ["brown", "light"]],
            ["red", ["purple", "light"]],
            ["green", ["yellow", "light"]],
            ["brown", ["blue", "light"]],
        ],
        [
            ["red", None],
            ["orange", None],
            ["pink", None],
            ["green", None],
            ["blue", None],
            ["yellow", None],
            ["brown", None],
            ["purple", None],
        ],
        [
            ["green", None],
            ["pink", None],
            ["orange", None],
            ["red", None],
            ["purple", None],
            ["brown", None],
            ["yellow", None],
            ["blue", None],
        ],
        [
            ["pink", None],
            ["purple", None],
            ["blue", None],
            ["orange", None],
            ["brown", None],
            ["green", None],
            ["red", None],
            ["yellow", None],
        ],
        [
            ["yellow", None],
            ["red", None],
            ["green", None],
            ["brown", None],
            ["orange", None],
            ["blue", None],
            ["purple", None],
            ["pink", None],
        ],
        [
            ["blue", None],
            ["yellow", None],
            ["brown", None],
            ["purple", None],
            ["red", None],
            ["orange", None],
            ["pink", None],
            ["green", None],
        ],
        [
            ["purple", None],
            ["brown", None],
            ["yellow", None],
            ["blue", None],
            ["green", None],
            ["pink", None],
            ["orange", None],
            ["red", None],
        ],
        [
            ["brown", ["blue", "dark"]],
            ["green", ["pink", "dark"]],
            ["red", ["red", "dark"]],
            ["yellow", ["orange", "dark"]],
            ["pink", ["brown", "dark"]],
            ["purple", ["purple", "dark"]],
            ["blue", ["yellow", "dark"]],
            ["orange", ["green", "dark"]],
        ],
    ]

    state = next(state, [[7, 0], [1, 0]])
    pprint(state["board"])
    state = next(state, [[0, 2], [4, 6]])
    pprint(state["board"])
    state = next(state, [[7, 5], [1, 5]])
    pprint(state["board"])

    state = {
        "board": [
            [
                ["orange", ["brown", "light"]],
                ["blue", ["blue", "light"]],
                ["purple", ["purple", "light"]],
                ["pink", None],
                ["yellow", None],
                ["red", None],
                ["green", None],
                ["brown", None],
            ],
            [
                ["red", None],
                ["orange", None],
                ["pink", None],
                ["green", None],
                ["blue", None],
                ["yellow", None],
                ["brown", None],
                ["purple", None],
            ],
            [
                ["green", None],
                ["pink", ["green", "dark"]],
                ["orange", None],
                ["red", None],
                ["purple", None],
                ["brown", None],
                ["yellow", None],
                ["blue", None],
            ],
            [
                ["pink", None],
                ["purple", None],
                ["blue", None],
                ["orange", None],
                ["brown", None],
                ["green", None],
                ["red", None],
                ["yellow", None],
            ],
            [
                ["yellow", None],
                ["red", None],
                ["green", None],
                ["brown", None],
                ["orange", None],
                ["blue", None],
                ["purple", None],
                ["pink", None],
            ],
            [
                ["blue", None],
                ["yellow", None],
                ["brown", None],
                ["purple", None],
                ["red", None],
                ["orange", None],
                ["pink", None],
                ["green", None],
            ],
            [
                ["purple", None],
                ["brown", None],
                ["yellow", None],
                ["blue", None],
                ["green", ["orange", "light"]],
                ["pink", None],
                ["orange", None],
                ["red", None],
            ],
            [
                ["brown", None],
                ["green", None],
                ["red", None],
                ["yellow", ["yellow", "dark"]],
                ["pink", ["pink", "dark"]],
                ["purple", ["purple", "dark"]],
                ["blue", None],
                ["orange", None],
            ],
        ],
        "color": "green",
        "current": 0,
        "players": ["LUR", "FKY"],
    }

    try:
        state = next(state, [[2, 1], [1, 1]])
    except game.GameWin as e:
        print(e)
