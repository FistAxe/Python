import pygame as pg
import sys
#import TCG

pg.init()

WIDTH = 1280
HEIGHT = 768

SURF = pg.display.set_mode((WIDTH, HEIGHT))

WHITE = pg.Color(255, 255, 255)
BLACK = pg.Color(0, 0, 0)
BOARD_BG = pg.Color(230, 230, 255)
ROW_BG = pg.Color(200, 200, 255)
GY_BG = pg.Color(200, 200, 200)
SURF.fill(WHITE)

pg.display.set_caption('TCG')

FPS = pg.time.Clock()
FPS.tick(60)

RIGHT_MARGINE = 320
BOARD_MARGIN = 5
LINE_WIDTH = 3
HALFBOARD_WIDTH = WIDTH - RIGHT_MARGINE - 2*BOARD_MARGIN
HALFBOARD_HEIGHT = (HEIGHT - 2*BOARD_MARGIN)//2
ROW_HEIGHT = HALFBOARD_HEIGHT//2
ROW1 = BOARD_MARGIN
ROW2 = ROW1 + ROW_HEIGHT
ROW3 = ROW2 + ROW_HEIGHT
ROW4 = ROW3 + ROW_HEIGHT

CARD_SIZE = [100, 140]
card_back_image = pg.image.load('./image/card_back.png')

ZONE_MARGIN = 2
ZONE_SIZE = [CARD_SIZE[0] + 2*ZONE_MARGIN, CARD_SIZE[1] + 2*ZONE_MARGIN]

def card_on_zone(zone_pos:list):
    return [zone_pos[0] + ZONE_MARGIN, zone_pos[1] + ZONE_MARGIN]

board_rv = [BOARD_MARGIN, BOARD_MARGIN, HALFBOARD_WIDTH, HALFBOARD_HEIGHT*2]
board = pg.Surface((HALFBOARD_WIDTH, HALFBOARD_HEIGHT*2))
board.fill(WHITE)

half1_rv = [BOARD_MARGIN, BOARD_MARGIN + HALFBOARD_HEIGHT, HALFBOARD_WIDTH, HALFBOARD_HEIGHT]
half2_rv = [BOARD_MARGIN, BOARD_MARGIN, HALFBOARD_WIDTH, HALFBOARD_HEIGHT]
halfboard_template = pg.Surface((HALFBOARD_WIDTH, HALFBOARD_HEIGHT))
halfboard_template.fill(BOARD_BG)
pg.draw.rect(halfboard_template, BLACK, halfboard_template.get_rect(), LINE_WIDTH)

halfboard1 = halfboard_template.copy()
halfboard2 = halfboard_template.copy()

deck1_rv = [BOARD_MARGIN + HALFBOARD_WIDTH - ZONE_SIZE[0], ROW4, ZONE_SIZE[0], ZONE_SIZE[1]]
deck2_rv = [BOARD_MARGIN, ROW1, ZONE_SIZE[0], ZONE_SIZE[1]]
deck_template = pg.Surface((ZONE_SIZE[0], ZONE_SIZE[1]))
deck_template.fill(WHITE)
pg.draw.rect(deck_template, BLACK, deck_template.get_rect(), LINE_WIDTH)

deck1 = deck_template.copy()
deck2 = deck_template.copy()

gy1_rv = [BOARD_MARGIN + HALFBOARD_WIDTH - ZONE_SIZE[0], ROW3, ZONE_SIZE[0], ZONE_SIZE[1]]
gy2_rv = [BOARD_MARGIN, ROW2, ZONE_SIZE[0], ZONE_SIZE[1]]
gy_template = pg.Surface((ZONE_SIZE[0], ZONE_SIZE[1]))
gy_template.fill(GY_BG)
pg.draw.rect(gy_template, BLACK, gy_template.get_rect(), LINE_WIDTH)

gy1 = gy_template.copy()
gy2 = gy_template.copy()

mz1_rv = [BOARD_MARGIN + HALFBOARD_WIDTH/2 - ZONE_SIZE[0]/2, ROW3, ZONE_SIZE[0], ZONE_SIZE[1]]
mz2_rv = [BOARD_MARGIN + HALFBOARD_WIDTH/2 - ZONE_SIZE[0]/2, ROW2, ZONE_SIZE[0], ZONE_SIZE[1]]
mz_template = pg.Surface((ZONE_SIZE[0], ZONE_SIZE[1]))
mz_template.fill(WHITE)
pg.draw.rect(mz_template, BLACK, mz_template.get_rect(), LINE_WIDTH)

mz1 = mz_template.copy()
mz2 = mz_template.copy()

sz_template = pg.Surface((ZONE_SIZE[0], ZONE_SIZE[1]))
sz_template.fill(WHITE)
pg.draw.rect(sz_template, BLACK, sz_template.get_rect(), LINE_WIDTH)

row1_rv = [BOARD_MARGIN + ZONE_SIZE[0], ROW4, HALFBOARD_WIDTH - 2*ZONE_SIZE[0], ROW_HEIGHT - LINE_WIDTH]
row2_rv = [BOARD_MARGIN + ZONE_SIZE[0], ROW1 + LINE_WIDTH, HALFBOARD_WIDTH - 2*ZONE_SIZE[0], ROW_HEIGHT - LINE_WIDTH]
row1 = pg.Surface((HALFBOARD_WIDTH - 2*ZONE_SIZE[0], ROW_HEIGHT - LINE_WIDTH), pg.SRCALPHA)
for x in range(HALFBOARD_WIDTH - 2*ZONE_SIZE[0]):
    d = abs(x - (HALFBOARD_WIDTH - 2*ZONE_SIZE[0])/2)
    transparancy = 1 - d/(HALFBOARD_WIDTH - 2*ZONE_SIZE[0])*2
    pg.draw.line(row1, (200, 200, 250, 255*transparancy), (x, 0), (x, ROW_HEIGHT - LINE_WIDTH))

row2 = row1.copy()

gamecomponents: dict[str, pg.Rect] = {
    'board': None,
    'halfboard1': None,
    'halfboard2': None,
    'deck1': None,
    'deck2': None,
    'gy1': None,
    'gy2': None,
    'mainzone1': None,
    'mainzone2': None,
    'row1': None,
    'row2': None
    }

cardlist = {
    'deck1': [],
    'deck2': [],
    'mainzone1': [],
    'mainzone2': [],
    'gy1': [],
    'gy2': []
    }
for i in range(20):
    cardlist['deck1'].append(i)

hovering = []
clicking = []
unclicking = []
dragging = False

def screen_generator():
    SURF.fill(WHITE)
    gamecomponents['board'] = SURF.blit(board, board_rv)
    gamecomponents['halfboard1'] = SURF.blit(halfboard1, half1_rv)
    gamecomponents['halfboard2'] = SURF.blit(halfboard2, half2_rv)
    gamecomponents['deck1'] = SURF.blit(deck1, deck1_rv)
    gamecomponents['deck2'] = SURF.blit(deck2, deck2_rv)
    gamecomponents['gy1'] = SURF.blit(gy1, gy1_rv)
    gamecomponents['gy2'] = SURF.blit(gy2, gy2_rv)
    gamecomponents['mainzone1'] = SURF.blit(mz1, mz1_rv)
    gamecomponents['mainzone2'] = SURF.blit(mz2, mz2_rv)
    gamecomponents['row1'] = SURF.blit(row1, row1_rv)
    gamecomponents['row2'] = SURF.blit(row2, row2_rv)
    for card in range(len(cardlist['deck1'])):
        SURF.blit(card_back_image, (card_on_zone(deck1_rv)[0], card_on_zone(deck1_rv)[1] + 4*card))
    for card in range(len(cardlist['mainzone1'])):
        SURF.blit(card_back_image, (card_on_zone(mz1_rv)[0], card_on_zone(mz1_rv)[1] + 4*card))
    for card in range(len(cardlist['gy1'])):
        SURF.blit(card_back_image, (card_on_zone(gy1_rv)[0], card_on_zone(gy1_rv)[1] + 4*card))
    if dragging:
        gamecomponents['sample card'] = SURF.blit(
            card_back_image, tuple(sum(elem) for elem in zip(pg.mouse.get_pos(), (-50, -70)))
            )

#input player 1, 2 {name, deck, etc}
#player1 = TCG.HalfBoard()
#player2 = TCG.HalfBoard()
#game = TCG.Board(player1, player2)

#gameplay = game.play()
#next(gameplay)

screen_generator()

REFRESH = True

while REFRESH:
    frame_hovering = []
    frame_clicking = []
    frame_unclicking = []
    for event in pg.event.get():
        if event.type == pg.QUIT:
            REFRESH = False
            continue

        if event.type == pg.MOUSEMOTION:
            #print('moved')
            for key in gamecomponents:
                if gamecomponents[key].collidepoint(pg.mouse.get_pos()):
                    print(f'you are on {key}.')
                    #frame_hovering.append(key)

        if event.type == pg.MOUSEBUTTONDOWN:
            print('pressed')
            for key in gamecomponents:
                if gamecomponents[key].collidepoint(pg.mouse.get_pos()):
                    print(f'you clicked {key}.')
                    #frame_clicking.append(key)
                    for place in ['deck1', 'deck2', 'mainzone1', 'mainzone2', 'gy1', 'gy2']:
                        if place == key and len(cardlist[key]) > 0:
                            cardlist[key].pop()
                            dragging = True

        if event.type == pg.MOUSEBUTTONUP:
            print('unpressed')
            for key in gamecomponents:
                if gamecomponents[key].collidepoint(pg.mouse.get_pos()):
                    print(f'you dragged to {key}.')
                    #frame_unclicking.append(key)
                    for component in [
                        'mainzone1',
                        'mainzone2',
                        'gy1',
                        'gy2']:
                        if dragging == True and key == component:
                            cardlist[key].append(len(cardlist[key]))
                            dragging = False
    
    # if frame_hovering == hovering:
    #   hovering = []
    # else:
    #   hovering = frame_hovering

    # gameplay.send([hovering, clicking, unclicking])
    screen_generator()
    pg.display.update()

pg.quit()
sys.exit()