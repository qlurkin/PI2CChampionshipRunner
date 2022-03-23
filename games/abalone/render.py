from PIL import Image, ImageDraw
from math import cos, sin, pi

# WIDTH = 600
# HEIGHT = 600
# SIZE = (WIDTH, HEIGHT)
LINEWIDTH = 5

def hexagone(draw, center, radius, color, angle=0):
	xc, yc = center
	points = []
	for i in range(6):
		x = xc + radius * cos(angle + i*pi/3)
		y = yc + radius * sin(angle + i*pi/3)
		points.append((x, y))
	points.append(points[0])
	draw.line(points, color, LINEWIDTH)

def drawCircle(draw, center, radius, fill, outline):
	xc, yc = center
	draw.ellipse([xc-radius, yc-radius, xc+radius, yc+radius], fill, outline, LINEWIDTH)


def render(state, side=600):
	global LINEWIDTH
	LINEWIDTH = round(6/600*side)
	SIZE = (side, side)
	res = Image.new('RGBA', SIZE, (50, 50, 50))
	draw = ImageDraw.Draw(res)

	hexagone(draw, (300/600*side, 300/600*side), 280/600*side, (150, 150, 150))

	size = 59/600*side
	lineVector = (size*cos(2*pi/3), size*sin(2*pi/3))
	colVector = (size, 0)

	xOffset = side/2 - 4 * lineVector[0] - 4 * colVector[0]
	yOffset = side/2 - 4 * lineVector[1] - 4 * colVector[1]

	def getCoord(line, col):
		return (xOffset + line*lineVector[0] + col*colVector[0], yOffset + line*lineVector[1] + col*colVector[1])

	for l in range(9):
		for c in range(9):
			if abs(c-l) < 5:
				hexagone(draw, getCoord(l, c), 27/600*side, (150, 150, 150), pi/6)

	if state is None:
		return res

	white = 0
	black = 0
	for l in range(9):
		for c in range(9):
			if state['board'][l][c] == 'W':
				drawCircle(draw, getCoord(l, c), 24/600*side, (255, 255, 255), (0, 0, 0))
				white += 1
			if state['board'][l][c] == 'B':
				drawCircle(draw, getCoord(l, c), 24/600*side, (0, 0, 0), (255, 255, 255))
				black += 1

	for i in range(14 - white):
		drawCircle(draw, (25/600*side + 60/600*side * i, 575/600*side), 24/600*side, (255, 255, 255), (0, 0, 0))

	for i in range(14 - black):
		drawCircle(draw, (575/600*side - 60/600*side * i, 25/600*side), 24/600*side, (0, 0, 0), (255, 255, 255))

	return res

if __name__=='__main__':
	state = {
		'players': ['LUR', 'LRG'],
		'current': 0,
		'board': [
			['W', 'W', 'W', 'W', 'W', 'X', 'X', 'X', 'X'],
			['W', 'W', 'W', 'W', 'W', 'W', 'X', 'X', 'X'],
			['E', 'E', 'W', 'W', 'W', 'E', 'E', 'X', 'X'],
			['E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'X'],
			['E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E'],
			['X', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E'],
			['X', 'X', 'E', 'E', 'B', 'B', 'B', 'E', 'E'],
			['X', 'X', 'X', 'B', 'B', 'B', 'B', 'B', 'B'],
			['X', 'X', 'X', 'X', 'B', 'B', 'B', 'B', 'B']
		]
	}
	image = render(None)
	image.save('image.png')
