from PIL import Image, ImageDraw
import os

root = os.path.dirname(__file__)


def draw_piece(draw, piece, center, side):
    if piece is None:
        return

    size = 0.8 * side / 8  # Big
    if "S" in piece:
        size = 0.4 * side / 8  # Small
    color = (0, 128, 255)  # Dark
    if "L" in piece:
        color = (255, 255, 0)  # Light
    weight = color  # Full
    if "E" in piece:
        weight = None  # Empty
    shape = 4
    if "C" in piece:
        shape = 20

    draw.regular_polygon(
        (center, size), shape, rotation=0, fill=weight, outline=color, width=5
    )


def render(state, side=600):
    WIDTH = side
    HEIGHT = side
    SIZE = (WIDTH, HEIGHT)
    LINEWIDTH = 5

    res = Image.new("RGBA", SIZE, (50, 50, 50))
    draw = ImageDraw.Draw(res)
    draw.line(
        [(WIDTH // 5, HEIGHT // 5), (WIDTH // 5, HEIGHT)], (200, 200, 200), LINEWIDTH
    )
    draw.line(
        [(2 * WIDTH // 5, HEIGHT // 5), (2 * WIDTH // 5, HEIGHT)],
        (200, 200, 200),
        LINEWIDTH,
    )
    draw.line(
        [(3 * WIDTH // 5, HEIGHT // 5), (3 * WIDTH // 5, HEIGHT)],
        (200, 200, 200),
        LINEWIDTH,
    )
    draw.line(
        [(0, 2 * HEIGHT // 5), (4 * WIDTH // 5, 2 * HEIGHT // 5)],
        (200, 200, 200),
        LINEWIDTH,
    )
    draw.line(
        [(0, 3 * HEIGHT // 5), (4 * WIDTH // 5, 3 * HEIGHT // 5)],
        (200, 200, 200),
        LINEWIDTH,
    )
    draw.line(
        [(0, 4 * HEIGHT // 5), (4 * WIDTH // 5, 4 * HEIGHT // 5)],
        (200, 200, 200),
        LINEWIDTH,
    )

    if state is None:
        return res

    startx = WIDTH // 10
    starty = HEIGHT // 10
    stepx = WIDTH // 5
    stepy = HEIGHT // 5

    draw_piece(draw, state["piece"], (startx + 4 * stepx, starty), 4 * side // 5)

    starty += stepy

    for i, elem in enumerate(state["board"]):
        x = i % 4
        y = i // 4

        draw_piece(draw, elem, (startx + x * stepx, starty + y * stepy), 4 * side // 5)

    return res


if __name__ == "__main__":
    pieces = set()
    for size in ["B", "S"]:
        for color in ["D", "L"]:
            for weight in ["E", "F"]:
                for shape in ["C", "P"]:
                    pieces.add(frozenset({size, color, weight, shape}))

    state = {
        "players": ["LUR", "FKY"],
        "current": 0,
        "board": list(pieces),
        "piece": "BDEC",
    }

    state = {
        "players": ["LUR", "FKY"],
        "current": 0,
        "board": [
            None,
            "BDEC",
            None,
            "SDFP",
            None,
            None,
            None,
            None,
            None,
            "SLFC",
            None,
            None,
            "BLFP",
            "BLEC",
            None,
            None,
        ],
        "piece": "BLEP",
    }

    image = render(state, 800)
    image.save("image.png")
