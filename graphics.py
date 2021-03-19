from chat import getChats
import pygame
from championship import getState, getAllPlayers
from match import getMatch

pygame.init()

screenSize = (1280, 800)

nameFont = pygame.font.Font('font/Steelflight/Steelflight.ttf', 16)
nameFont.set_bold(True)
messageFont = pygame.font.Font('font/Steelflight/Steelflight.ttf', 16)
pointFont = pygame.font.Font('font/Steelflight/Steelflight.ttf', 24)
pointFont.set_bold(True)
dimmedFont = pygame.font.Font('font/Steelflight/Steelflight.ttf', 8)
vsFont = pygame.font.Font('font/Steelflight/Steelflight.ttf', 56)
vsFont.set_bold(True)
playerFont = pygame.font.Font('font/Steelflight/Steelflight.ttf', 32)
playerFont.set_bold(True)

aaText = False

def pilImageToSurface(pilImage):
	return pygame.image.fromstring(pilImage.tobytes(), pilImage.size, pilImage.mode).convert()

def drawClient(client):
	res = pygame.Surface((200, 58))
	res.fill((0, 0, 0))
	pygame.draw.line(res, (255, 255, 255), (0, 57), (200, 57))

	name = nameFont.render(client['name'], aaText, (255, 255, 255))
	res.blit(name, (10, 10))

	address = dimmedFont.render('{}:{}'.format(*(client['address'])), aaText, (100, 100, 100))
	res.blit(address, (10, 30))

	points = pointFont.render(str(client['points']), aaText, (255, 255, 255))
	res.blit(points, points.get_rect(midright=(190, 30)))

	stat = dimmedFont.render('#{}, BM:{}'.format(client['matchCount'], client['badMoves']), aaText, (100, 100, 100))
	res.blit(stat, (10, 40))

	return res

def drawText(text, width, font, color):
	words = text.split(' ')
	space = font.size(' ')[0]  # The width of a space.
	
	surfaces = {}

	x, y = 0, 0
	for word in words:
		word_surface = font.render(word, aaText, color)
		word_width, word_height = word_surface.get_size()
		if x + word_width >= width:
			x = 0  # Reset the x.
			y += word_height  # Start on new row.
		surfaces[x, y] = word_surface
		#surface.blit(word_surface, (x, y))
		x += word_width + space

	res = pygame.Surface((width, y+word_height))
	for pos, surface in surfaces.items():
		res.blit(surface, pos)
	
	return res

def drawChat(chat):
	name = nameFont.render(chat['name'], aaText, (255, 255, 255))
	msg = drawText(chat['message'], 280, messageFont, (200, 200, 200))
	msgHeight = msg.get_size()[1]
	res = pygame.Surface((300, msgHeight + 40))
	res.blit(name, (10, 10))
	res.blit(msg, (10, 30))

	return res

def render(state, stateImage):
	players = getAllPlayers(state)
	matchState = getMatch()
	res = pygame.Surface(screenSize)
	res = res.convert()
	res.fill((0, 0, 0))
	pygame.draw.line(res, (255, 255, 255), (200, 0), (200, screenSize[1]))
	pygame.draw.line(res, (255, 255, 255), (screenSize[0]-300, 0), (screenSize[0]-300, screenSize[1]))

	y = 0
	for i, client in enumerate(sorted(players, key = lambda cl: -cl['points'])):
		clientSurface = drawClient(client)
		res.blit(clientSurface, (0, y))
		y += clientSurface.get_rect().size[1]

	y = screenSize[1]
	for chat in reversed(getChats()):
		chatSurface = drawChat(chat)
		chatPos = chatSurface.get_rect(bottomleft=(screenSize[0]-299, y))
		res.blit(chatSurface, chatPos)
		y -= chatSurface.get_rect().size[1]

	center = screenSize[0]//2-50
	
	if matchState is not None:
		vs = vsFont.render('VS', aaText, (255, 0, 0))
		res.blit(vs, vs.get_rect(midtop=(center+5, 15)))
		vs = vsFont.render('VS', aaText, (255, 255, 0))
		res.blit(vs, vs.get_rect(midtop=(center, 10)))

		player1 = playerFont.render(matchState['players'][0], aaText, (255, 255, 255))
		res.blit(player1, player1.get_rect(midright=(center-60, 45)))

		player2 = playerFont.render(matchState['players'][1], aaText, (255, 255, 255))
		res.blit(player2, player2.get_rect(midleft=(center+60, 45)))

	if stateImage is not None:
		stateSurface = pilImageToSurface(stateImage)
		stateSurfacePos = stateSurface.get_rect(center=(center, screenSize[1]//2+30))
		res.blit(stateSurface, stateSurfacePos)

	return res

def ui(gameName, gameRender):
	screen = pygame.display.set_mode(screenSize)
	pygame.display.set_caption('{} Championship'.format(gameName.capitalize()))

	clock = pygame.time.Clock()

	while True:
		clock.tick(60)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				return

		surface = render(getState(), gameRender(getMatch()))

		screen.blit(surface, (0, 0))
		pygame.display.flip()