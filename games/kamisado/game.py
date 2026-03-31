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
    ["", "", "", "", "", "", "", ""],  # 19
    ["", "", "", "", "", "", "", ""],  # 20
    ["", "", "", "", "", "", "", ""],  # 21
    ["", "", "", "", "", "", "", ""],  # 22
    ["", "", "", "", "", "", "", ""],  # 23
    ["", "", "", "", "", "", "", ""],  # 24
    ["", "", "", "", "", "", "", ""],  # 25
    ["", "", "", "", "", "", "", ""],  # 26
    ["", "", "", "", "", "", "", ""],  # 27
    ["", "", "", "", "", "", "", ""],  # 28
    ["", "", "", "", "", "", "", ""],  # 29
    ["", "", "", "", "", "", "", ""],  # 30
    ["", "", "", "", "", "", "", ""],  # 31
    ["", "", "", "", "", "", "", ""],  # 32
    ["", "", "", "", "", "", "", ""],  # 33
    ["", "", "", "", "", "", "", ""],  # 34
    ["", "", "", "", "", "", "", ""],  # 35
    ["", "", "", "", "", "", "", ""],  # 36
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

        if len(move) != 2:
            raise game.BadMove("A move must contains 2 positions.")

        for i in range(2):
            if len(move[i]) != 2:
                raise game.BadMove("A position must contains 2 coordinates.")

            for j in range(2):
                if isinstance(move[i][j], int):
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
        new_board[end_row][end_col][TILE] = new_board[start_col][start_row][TILE]
        new_board[start_col][start_row][TILE] = None

        other = (current + 1) % 2

        next_color = new_board[end_row][end_col][COLOR]
        next_tile = find_tile(new_board, next_color, KINDS[other])

        if end_row == END_ROW[KINDS[current]]:
            raise game.GameWin(
                current,
                {
                    "players": players,
                    "current": current,
                    "color": color,
                    "board": new_board,
                },
            )

        if blocked(new_board, next_tile):
            nr, nc = next_tile
            next_tile = find_tile(new_board, new_board[nr][nc][COLOR], KINDS[current])
            if blocked(new_board, next_tile):
                # Deadlock !!
                raise game.GameWin(
                    other,
                    {
                        "players": players,
                        "current": other,
                        "color": next_color,
                        "board": new_board,
                    },
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
    state, next = Game(["LUR", "FKY"])
    pprint(state)
