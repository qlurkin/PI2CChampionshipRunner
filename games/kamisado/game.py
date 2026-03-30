from games import game

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
    ["", "", "", "", "", "", "", ""],  # 7
    ["", "", "", "", "", "", "", ""],  # 8
    ["", "", "", "", "", "", "", ""],  # 9
    ["", "", "", "", "", "", "", ""],  # 10
    ["", "", "", "", "", "", "", ""],  # 11
    ["", "", "", "", "", "", "", ""],  # 12
    ["", "", "", "", "", "", "", ""],  # 13
    ["", "", "", "", "", "", "", ""],  # 14
    ["", "", "", "", "", "", "", ""],  # 15
    ["", "", "", "", "", "", "", ""],  # 16
    ["", "", "", "", "", "", "", ""],  # 17
    ["", "", "", "", "", "", "", ""],  # 18
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


def kamisado(players):
    if len(players) != 2:
        raise game.BadGameInit("Tic Tac Toe must be played by 2 players")

    state = {}

    def next(state, move):
        return state

    return state, next


Game = kamisado
