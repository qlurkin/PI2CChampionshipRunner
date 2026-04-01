if __name__ == "__main__":
    import os
    import sys

    sys.path.append(os.getcwd())


from PIL import Image, ImageDraw

COLORS = {
    "orange": (255, 140, 0),
    "blue": (135, 206, 235),
    "purple": (175, 0, 175),
    "pink": (255, 192, 203),
    "yellow": (255, 215, 0),
    "red": (255, 42, 42),
    "green": (0, 200, 0),
    "brown": (169, 99, 49),
    "dark": (0, 0, 0),
    "light": (255, 255, 255),
}


def render(state, side=600):
    WIDTH = side
    HEIGHT = side
    SIZE = (WIDTH, HEIGHT)
    MARGIN = 20
    HALFGAP = 1
    CELLSIDE = ((side - 2 * MARGIN) / 8) - 2 * HALFGAP

    res = Image.new("RGBA", SIZE, (50, 50, 50))
    draw = ImageDraw.Draw(res)

    board = state["board"]

    for r, row in enumerate(board):
        for c, cell in enumerate(row):
            color, tile = cell
            draw.rectangle(
                [
                    [
                        MARGIN + c * (CELLSIDE + 2 * HALFGAP) + HALFGAP,
                        MARGIN + r * (CELLSIDE + 2 * HALFGAP) + HALFGAP,
                    ],
                    [
                        MARGIN + c * (CELLSIDE + 2 * HALFGAP) + HALFGAP + CELLSIDE,
                        MARGIN + r * (CELLSIDE + 2 * HALFGAP) + HALFGAP + CELLSIDE,
                    ],
                ],
                fill=COLORS[color],
            )
            if tile is not None:
                tile_color, kind = tile
                draw.circle(
                    [
                        MARGIN + c * (CELLSIDE + 2 * HALFGAP) + HALFGAP + CELLSIDE / 2,
                        MARGIN + r * (CELLSIDE + 2 * HALFGAP) + HALFGAP + CELLSIDE / 2,
                    ],
                    CELLSIDE / 2 - 2 * HALFGAP,
                    fill=COLORS[kind],
                )
                draw.circle(
                    [
                        MARGIN + c * (CELLSIDE + 2 * HALFGAP) + HALFGAP + CELLSIDE / 2,
                        MARGIN + r * (CELLSIDE + 2 * HALFGAP) + HALFGAP + CELLSIDE / 2,
                    ],
                    CELLSIDE / 2 - 4 * HALFGAP,
                    fill=COLORS[tile_color],
                )

    return res


if __name__ == "__main__":
    from games.kamisado.game import Game

    state, next = Game(["lUR", "FKY"])

    im = render(state)
    im.save("test.png")
