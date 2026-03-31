from PIL import Image, ImageDraw


def render(state, side=600):
    WIDTH = side
    HEIGHT = side
    SIZE = (WIDTH, HEIGHT)

    res = Image.new("RGBA", SIZE, (50, 50, 50))

    return res
