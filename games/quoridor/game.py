import copy
import numpy as np
#from render import *
import re
from games import game
# state representation
# {
#   "players": ["LUR", "FKY"],
#   "current": 0,
#   "blockers": [10, 10],
#   "board": <2D list 17x17>
# }

# move represenation
# {
#     "type" : "pawn" or "blocker"
#     "position" : [[2,4]] or [[0,1],[2,1]]
# }

# Global parameters

number_tiles_length = 9
number_blockers_per_player = 10

# The board representation has to contain a possible blocker between each tile
board_length = number_tiles_length * 2 - 1
max_index = board_length-1

# Board tile values
PAWN1 = 0
PAWN2 = 1
EMPTY_PAWN = 2
EMPTY_BLOCKER = 3
BLOCKER = 4
IMP = 5  # for places where no blockers and pawns can be

# Create a new board a game can start on


def create_new_board():
    board = np.ones((board_length, board_length)) * EMPTY_PAWN
    board[0, number_tiles_length-1] = PAWN1
    board[-1, number_tiles_length-1] = PAWN2
    for i in range(1, max_index, 2):
        for j in range(1, max_index, 2):
            board[i, j] = IMP
    for i in range(0, board_length, 2):
        for j in range(1, board_length, 2):
            board[i, j] = EMPTY_BLOCKER
            board[j, i] = EMPTY_BLOCKER
    return board


def Quoridor(players):
    if len(players) != 2:
        raise game.BadGameInit("We only support 2 players Game")
    board = create_new_board().tolist()
    blockers = [number_blockers_per_player, number_blockers_per_player]
    state = {
        "players": players,
        "current": 0,
        "blockers": blockers,
        "board": board,
    }

    def next(state, move):
        # create the new state and apply the move
        new_state = copy.deepcopy(state)

        # map 2D list to numpy array
        new_state["board"] = np.array(state["board"])

        # check if the move is valid
        check_valid_move(new_state, move)

        if move["type"] == "pawn":
            move_pawn(new_state["board"],
                      new_state["current"], move["position"][0])
            if is_won(new_state):
                raise game.GameWin(
                    new_state['current'], new_state)
        else:
            add_blocker(new_state["board"], move["position"])
            new_state["blockers"][new_state["current"]] -= 1
        new_state["current"] = other_pawn(new_state["current"])

        # map back numpy array two 2D list
        new_state["board"] = new_state["board"].tolist()
        return new_state
    return state, next


def check_valid_move(state, move):
    if move is None:
        raise game.BadMove("None is not a valid Move")

    # check for the types, the keys and in board positions
    try:
        assert isinstance(move["type"], str)
        assert isinstance(move["position"], list)
        if move["type"] not in ["pawn", "blocker"]:
            raise game.BadMove("Unknown move type: "+move["type"])
        for position, index in zip(move["position"], range(len(move["position"]))):
            assert isinstance(position, list)
            # make position tuple to be hashable
            move["position"][index] = tuple(position)
            if not check_inboard_position(position):
                raise game.BadMove("Move position not in the board")
    except KeyError as err:
        raise game.BadMove("Missing key {}".format(err))
    except AssertionError as err:
        raise game.BadMove("Wrong type {}".format(err))

    # check for valid position for a pawn or a blocker
    if move["type"] == "pawn":
        check_valid_pawn(state, move)
    if move["type"] == "blocker":
        check_valid_blocker(state, move)


def check_valid_blocker(state, move):
    # check if the player has some blockers left
    if state["blockers"][state["current"]] <= 0:
        raise game.BadMove("No more blocker available for this player")
    # check if the positions contain two elements
    if len(move["position"]) != 2:
        raise game.BadMove("A blocker can only take two positions")
    # check if the positions corresponds to the one of a BLOCKER or an EMPTY_BLOCKER
    for position in move["position"]:
        if state["board"][position] == BLOCKER:
            raise game.BadMove("A position is already occupied by a blocker")
        if state["board"][position] != EMPTY_BLOCKER:
            raise game.BadMove("Unauthorized blocker position")
    # check if the blockers are adjacent
    position0 = move["position"][0]
    position1 = move["position"][1]
    if not ((position0[0] == position1[0] and abs(position1[1]-position0[1]) == 2 and position0[0] % 2 == 1) or
            (position0[1] == position1[1] and abs(position1[0]-position0[0]) == 2 and position0[1] % 2 == 1)):
        raise game.BadMove(
            "The two positions of your blocker are not adjacent")
    # check if there is already a blocker in the the orthogonal axis
    if position0[0] % 2 == 1:
        j = min(position0[1],position1[1])+1
        ortho_1 = (position0[0]-1,j)
        ortho_2 = (position0[0]+1,j)
        if check_inboard_position(ortho_1) and check_inboard_position(ortho_2):
            if state["board"][ortho_1] == BLOCKER and state["board"][ortho_2] == BLOCKER:
                raise game.BadMove("There is already a blocker on the horizontal axis")
    else:
        i = min(position0[0],position1[0])+1
        ortho_1 = (i,position0[1]-1)
        ortho_2 = (i,position0[1]+1)
        if check_inboard_position(ortho_1) and check_inboard_position(ortho_2):
            if state["board"][ortho_1] == BLOCKER and state["board"][ortho_2] == BLOCKER:
                raise game.BadMove("There is already a blocker on the vertical axis")

    # check if the game is still winnable by both players after adding the blockers
    board_after_move = np.copy(state["board"])
    add_blocker(board_after_move, move["position"])

    if not is_winnable(board_after_move):
        raise game.BadMove(
            "Your blocker prevent any possible victory a for a player")
    return True


def is_won(state):
    goal_pawn = [(0, i) if state["current"] == PAWN2 else (max_index, i)
                 for i in range(0, max_index+1, 2)]
    pawn_pos = pawn_position(state["board"], state["current"])
    return pawn_pos in goal_pawn


def is_winnable(board):
    board = np.copy(board)
    nbr_win = 0
    # BFS for each pawn to check if they can reach the winning condition
    for pawn in [PAWN1, PAWN2]:
        goal_pawn = {(0, i) if pawn == PAWN2 else (max_index, i)
                     for i in range(0, max_index+1, 2)}
        to_explore = next_positions(board, pawn)
        explored = set()
        while to_explore:
            current = to_explore.pop()
            move_pawn(board, pawn, current)
            new_positions = set(next_positions(board, pawn))
            if new_positions & goal_pawn:
                nbr_win += 1
                break
            explored |= {current}
            to_explore |= (new_positions - explored)
    return nbr_win == 2


def next_positions(board, pawn, stop_recursive=False):
    positions = set()
    pawn_pos = pawn_position(board, pawn)
    deltas = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    # check in the four possible directions
    for delta in deltas:
        # check if there is a wall or a blocker
        wall_checker = add_coord(pawn_pos, delta)
        if not check_inboard_position(wall_checker):
            continue
        if board[wall_checker] == BLOCKER:
            continue
        # check if there is another pawn
        pawn_checker = add_coord(wall_checker, delta)
        if not check_inboard_position(pawn_checker):
            continue
        if board[pawn_checker] == other_pawn(pawn):
            # if there is a pawn add the next positions of this pawn
            if stop_recursive:
                continue
            positions |= next_positions(
                board, other_pawn(pawn), stop_recursive=True)
        else:
            positions |= set([pawn_checker])
    return positions


def move_pawn(board, pawn, position):
    pawn_pos = pawn_position(board, pawn)
    board[pawn_pos] = EMPTY_PAWN
    board[position] = pawn


def other_pawn(pawn):
    return (pawn + 1) % 2


def pawn_position(board, pawn):
    pawn_pos = np.where(board == pawn)
    return (pawn_pos[0][0], pawn_pos[1][0])


def check_inboard_position(pawn_position):
    if (pawn_position[0] < 0 or pawn_position[1] < 0 or
       pawn_position[0] > max_index or pawn_position[1] > max_index):
        return False
    return True


def add_blocker(board, positions):
    board[positions[0]] = BLOCKER
    board[positions[1]] = BLOCKER


def add_coord(position, delta):
    return (position[0] + delta[0], position[1] + delta[1])


def check_valid_pawn(state, move):

    if len(move["position"]) != 1:
        raise game.BadMove("A pawn move can only have one position")

    board = state["board"]
    new_positions = next_positions(board, state["current"])
    if move["position"][0] not in new_positions:
        raise game.BadMove("The new position of the pawn is not allowed")

    return True


Game = Quoridor

if __name__ == "__main__":

    state, next = Game(["LUR", "FKY"])
    try:
        while True:
            image = render(state)
            image.show()
            move_type = input('{} move [pawn or blocker]: '.format(
                state['players'][state['current']]))
            positions = []
            if move_type == "pawn":
                positions.append(
                    list(map(int, re.sub("[()\[\]]", "", input("What position?")).split(','))))
            elif move_type == "blocker":
                positions.append(
                    list(map(int, re.sub("[()\[\]]", "", input("What position?")).split(','))))
                positions.append(
                    list(map(int, re.sub("[()\[\]]", "", input("What position?")).split(','))))
            else:
                raise game.BadMove("Wrong Move")
            try:
                move = {"type": move_type, "position": positions}
                print(move)
                state = next(state, move)
            except game.BadMove as e:
                print(e)
    except game.GameWin as e:
        render(e.state['board'])
        print('{} win the game'.format(state['players'][e.winner]))
