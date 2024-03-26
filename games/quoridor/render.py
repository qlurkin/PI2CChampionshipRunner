from PIL import Image, ImageDraw
import numpy as np
## Global parameters

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

square_size = 50  # Size of each square in pixels
wall_thikness = 5  # Thickness of walls in pixels
board_color = "white"
wall_color = "black"
pawn1_color = "red"
pawn2_color = "blue"

# Function to draw the board


def render(state, side=450):
    board = state["board"]
    square_size = side // number_tiles_length

    image = Image.new("RGBA", (side, side), color=board_color)
    draw = ImageDraw.Draw(image)

    # Draw horizontal lines
    for i in range(number_tiles_length):
        draw.line([(0, i * square_size), (side,
                  i * square_size)], fill="black", width=1)

    # Draw vertical lines
    for i in range(number_tiles_length):
        draw.line([(i * square_size, 0), (i * square_size,
                  side)], fill="black", width=1)

    for j in range(board_length):
        for i in range(board_length):
            match board[j][i]:
                case 0:
                    draw_player(draw, (PAWN1, (i, j)), side)
                    continue
                case 1:
                    draw_player(draw, (PAWN2, (i, j)), side)
                    continue
                case 4:
                    draw_blocker(draw, (i, j), side)
                    continue
    return image

# Function to add players to the board


def draw_player(draw, player_position, side):
    square_size = side // number_tiles_length
    player, position = player_position
    x, y = position
    x //= 2
    y //= 2
    player_color = pawn1_color if player == 1 else pawn2_color
    draw.ellipse([(x * square_size + square_size // 4, y * square_size + square_size // 4),
                  (x * square_size + 3 * square_size // 4, y * square_size + 3 * square_size // 4)],
                 fill=player_color)

# Function to draw a wall


def draw_blocker(draw, wall, side):
    square_size = side // number_tiles_length
    wall_thikness = square_size // 10
    i, j = wall
    x = i // 2
    y = j // 2
    if i % 2 == 1:
        draw.rectangle([((x * square_size) - wall_thikness, (y) * square_size),
                        ((x * square_size) + wall_thikness, (y+1) * square_size)], fill=wall_color)
    else:
        draw.rectangle([(x * square_size, ((y+1) * square_size) - wall_thikness),
                        ((x + 1) * square_size, ((y+1) * square_size) + wall_thikness)], fill=wall_color)


def render_terminal(state):
    board = state["board"]
    line = ""
    for i in range(17):
        line += str(i)
        line += "  " if i < 10 else " "
    print(line)
    for row_idx, row in enumerate(board):
        line = str(row_idx)
        if row_idx % 2 == 0:
            for elem_idx, elem in enumerate(row):
                if elem_idx % 2 == 0:
                    character = "|{}|".format(state["players"][int(elem)]) if elem in [
                        PAWN1, PAWN2] else "|   |"
                else:
                    character = "x" if elem == BLOCKER else " "
                line += character
            print(" "+"+---+ " * 9)
            print(line)
            print(" "+"+---+ " * 9)
        else:
            for elem_idx, elem in enumerate(row):
                if elem_idx % 2 == 0:
                    character = "  x  " if elem == BLOCKER else "     "
                else:
                    character = " "
                line += character
            print(line)

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

if __name__ == "__main__":
    board = create_new_board().tolist()
    board[1][8] = BLOCKER
    # board[1][7] = BLOCKER
    image = render({"board": board, "players": [
                   "LUR", "FKY"], "current": PAWN1, })
    image.save('image.png')
    image.show()
