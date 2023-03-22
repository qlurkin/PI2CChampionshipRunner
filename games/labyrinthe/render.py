from PIL import Image, ImageDraw, ImageFont

font = ImageFont.truetype("arial.ttf", 20)


def letter(item):
    return chr(ord("A") + item)


def drawTile(draw: ImageDraw.ImageDraw, tile, i, j, side):
    draw.rounded_rectangle(
        xy=(j * side + 2, i * side + 2, j * side + side - 2, i * side + side - 2),
        radius=side / 8,
        width=0,
        fill=(224, 149, 88),
    )
    if tile["N"]:
        draw.rectangle(
            xy=(
                j * side + side / 2 - side / 4,
                i * side,
                j * side + side / 2 + side / 4,
                i * side + side / 2 + side / 4,
            ),
            fill=(50, 50, 50),
            width=0,
        )
    if tile["S"]:
        draw.rectangle(
            xy=(
                j * side + side / 2 - side / 4,
                i * side + side / 2 - side / 4,
                j * side + side / 2 + side / 4,
                i * side + side,
            ),
            fill=(50, 50, 50),
            width=0,
        )
    if tile["W"]:
        draw.rectangle(
            xy=(
                j * side,
                i * side + side / 2 - side / 4,
                j * side + side / 2 + side / 4,
                i * side + side / 2 + side / 4,
            ),
            fill=(50, 50, 50),
            width=0,
        )
    if tile["E"]:
        draw.rectangle(
            xy=(
                j * side + side / 2 - side / 4,
                i * side + side / 2 - side / 4,
                j * side + side,
                i * side + side / 2 + side / 4,
            ),
            fill=(50, 50, 50),
            width=0,
        )
    if tile["item"] is not None:
        draw.text(
            xy=(j * side + side / 2, i * side + side / 2),
            anchor="mm",
            text=letter(tile["item"]),
            font=font,
        )


def render(state, side=600):
    SIZE = (side, side)
    res = Image.new("RGBA", SIZE, (50, 50, 50))
    draw = ImageDraw.Draw(res)
    tileSide = side / 8
    drawTile(draw, state["tile"], 0, 7, tileSide)
    for index, tile in enumerate(state["board"]):
        i = index // 7
        j = index % 7
        drawTile(draw, tile, i + 1, j + 0.5, tileSide)
    draw.text(
        xy=(tileSide / 2, tileSide / 2),
        anchor="lm",
        font=font,
        text="Trg: {}        Rmn: {}".format(
            letter(state["target"]), state["remaining"][state["current"]]
        ),
    )
    p1x = state["positions"][0] % 7 * tileSide + tileSide
    p1y = state["positions"][0] // 7 * tileSide + tileSide + tileSide / 2
    r = tileSide / 4
    draw.ellipse(xy=(p1x - r, p1y - r, p1x + r, p1y + r), width=5, outline=(255, 242, 0))

    p2x = state["positions"][1] % 7 * tileSide + tileSide
    p2y = state["positions"][1] // 7 * tileSide + tileSide + tileSide / 2
    r = tileSide / 4
    draw.ellipse(xy=(p2x - r, p2y - r, p2x + r, p2y + r), width=5, outline=(0, 162, 232))
    return res


if __name__ == "__main__":
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
        "remaining": [4, 4],
    }
    image = render(state)
    image.save("image.png")
