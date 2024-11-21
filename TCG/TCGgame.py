import pygame as pg
import TCG

pg.init()

SURF = pg.display.set_mode((1280, 768))

WHITE = pg.Color(255, 255, 255)
SURF.fill(WHITE)

pg.display.set_caption('TCG')

FPS = pg.time.Clock()
FPS.tick(60)

def screen_generator():
    pass

#input player 1, 2 {name, deck, etc}
player1 = TCG.HalfBoard()
player2 = TCG.HalfBoard()
game = TCG.Board(player1, player2)

resume = game.play()

REFRESH = True
while REFRESH:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            REFRESH = False
            continue

        if event.type == pg.MOUSEMOTION:
            print('moved')

        if event.type == pg.MOUSEBUTTONDOWN:
            print('pressed')

        if event.type == pg.MOUSEBUTTONUP:
            print('unpressed')
    screen_generator(game)
    pg.display.update()

pg.quit()