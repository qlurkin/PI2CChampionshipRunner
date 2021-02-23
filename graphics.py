from clients import add
import pygame

screenSize = (1280, 800)

nameFont = pygame.font.Font('font/Steelflight/Steelflight.ttf', 16)
nameFont.set_bold(True)
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

def render(state, clients, stateImage):
	res = pygame.Surface(screenSize)
	res = res.convert()
	res.fill((0, 0, 0))
	pygame.draw.line(res, (255, 255, 255), (200, 0), (200, screenSize[1]))
	pygame.draw.line(res, (255, 255, 255), (screenSize[0]-300, 0), (screenSize[0]-300, screenSize[1]))

	y = 0
	for i, client in enumerate(sorted(clients, key = lambda cl: -cl['points'])):
		clientSurface = drawClient(client)
		res.blit(clientSurface, (0, y))
		y += clientSurface.get_rect().size[1]

	if state is not None:
		center = screenSize[0]//2-50
		vs = vsFont.render('VS', aaText, (255, 0, 0))
		res.blit(vs, vs.get_rect(midtop=(center+5, 15)))
		vs = vsFont.render('VS', aaText, (255, 255, 0))
		res.blit(vs, vs.get_rect(midtop=(center, 10)))

		player1 = playerFont.render(state['players'][0], aaText, (255, 255, 255))
		res.blit(player1, player1.get_rect(midright=(center-60, 45)))

		player2 = playerFont.render(state['players'][1], aaText, (255, 255, 255))
		res.blit(player1, player1.get_rect(midleft=(center+60, 45)))

		stateSurface = pilImageToSurface(stateImage)
		stateSurfacePos = stateSurface.get_rect(center=(center, screenSize[1]//2+40))
		res.blit(stateSurface, stateSurfacePos)

	return res