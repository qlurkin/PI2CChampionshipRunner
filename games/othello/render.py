from PIL import Image, ImageDraw

def coord(index):
    return index // 8, index % 8

def drawCircle(draw, center, radius, fill, outline, linewidth):
	xc, yc = center
	draw.ellipse([xc-radius, yc-radius, xc+radius, yc+radius], fill, outline, linewidth)

def render(state, side=300):
    res = Image.new('RGBA', (side, side), (50, 50, 50))
    draw = ImageDraw.Draw(res)

    caseSide = side/9
    offset = (side - 8*caseSide) / 2
    LINEWIDTH = round(side/120)

    for i in range(9):
        draw.line([(offset + i*caseSide, offset), (offset + i*caseSide, side-offset)], (200, 200, 200), LINEWIDTH)

    for i in range(9):
        draw.line([(offset, offset + i*caseSide), (side-offset, offset + i*caseSide)], (200, 200, 200), LINEWIDTH)

    for case in state['board'][0]:
        l, c = coord(case)
        drawCircle(draw, (offset+caseSide/2+c*caseSide+LINEWIDTH/2, offset+caseSide/2+l*caseSide+LINEWIDTH/2), caseSide*0.85/2, (0, 0, 0), (255, 255, 255), LINEWIDTH)
    for case in state['board'][1]:
        l, c = coord(case)
        drawCircle(draw, (offset+caseSide/2+c*caseSide+LINEWIDTH/2, offset+caseSide/2+l*caseSide+LINEWIDTH/2), caseSide*0.85/2, (255, 255, 255), (0, 0, 0), LINEWIDTH)

    return res

if __name__ == '__main__':
    state = {
        'players': ['LUR', 'HSL'],
        'current': 0,
        'board': [
            [28, 35],
            [27, 36]
        ]
    }

    image = render(state)

    image.save('othello.png')