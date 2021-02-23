from PIL import Image, ImageDraw
import os

root = os.path.dirname(__file__)

cross = Image.open(os.path.join(root, 'cross.png'))
circle = Image.open(os.path.join(root, 'circle.png'))

WIDTH = 600
HEIGHT = 600
SIZE = (WIDTH, HEIGHT)
LINEWIDTH = 5

def render(state):
	if state is None:
		return

	res = Image.new('RGBA', SIZE, (50, 50, 50))
	draw = ImageDraw.Draw(res)
	draw.line([(WIDTH//3, 0), (WIDTH//3, HEIGHT)], (200, 200, 200), LINEWIDTH)
	draw.line([(2*WIDTH//3, 0), (2*WIDTH//3, HEIGHT)], (200, 200, 200), LINEWIDTH)
	draw.line([(0, HEIGHT//3), (WIDTH, HEIGHT//3)], (200, 200, 200), LINEWIDTH)
	draw.line([(0, 2*HEIGHT//3), (WIDTH, 2*HEIGHT//3)], (200, 200, 200), LINEWIDTH)

	startx = WIDTH//6 - cross.size[0]//2
	starty = HEIGHT//6 - cross.size[1]//2
	stepx = WIDTH//3
	stepy = HEIGHT//3
	for i, elem in enumerate(state['board']):
		x = i%3
		y = i//3
		if elem == 'X':
			res.paste(cross, (startx+x*stepx, starty+y*stepy), cross)
		elif elem == 'O':
			res.paste(circle, (startx+x*stepx, starty+y*stepy), circle)

	return res

if __name__=='__main__':
	image = render(None)
	image.save('image.png')
