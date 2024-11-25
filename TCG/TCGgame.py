import pygame as pg
import sys
import TCG as TCG

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

RIGHT_MARGINE = 400
BOARD_MARGIN = 5
LINE_WIDTH = 3
HALFBOARD_WIDTH = WIDTH - RIGHT_MARGINE - 2*BOARD_MARGIN
ROW_HEIGHT = (HEIGHT - 2*BOARD_MARGIN)//6
HALFBOARD_HEIGHT = ROW_HEIGHT*2

ROW1 = BOARD_MARGIN
ROW2 = ROW1 + ROW_HEIGHT
ROW3 = ROW2 + ROW_HEIGHT
ROW4 = ROW3 + ROW_HEIGHT
ROW5 = ROW4 + ROW_HEIGHT
ROW6 = ROW5 + ROW_HEIGHT

CARD_SIZE = [90, 120]
card_back_image = pg.image.load('./image/card_back.png').convert()
TITLE_FONT = pg.font.SysFont('Gulim', 40)
EXP_FONT = pg.font.SysFont('Gulim', 15)

ZONE_MARGIN = 2
ZONE_SIZE = [CARD_SIZE[0] + 2*ZONE_MARGIN, CARD_SIZE[1] + 2*ZONE_MARGIN]
SUBZONE_MARGIN = 30

def card_on_zone(zone_pos:list):
    return [zone_pos[0] + ZONE_MARGIN, zone_pos[1] + ZONE_MARGIN]

board_rv = [BOARD_MARGIN, ROW2, HALFBOARD_WIDTH, HALFBOARD_HEIGHT*2]
board = pg.Surface((HALFBOARD_WIDTH, HALFBOARD_HEIGHT*2))
board.fill(WHITE)

half1_rv = [BOARD_MARGIN, ROW4, HALFBOARD_WIDTH, HALFBOARD_HEIGHT]
half2_rv = [BOARD_MARGIN, ROW2, HALFBOARD_WIDTH, HALFBOARD_HEIGHT]
halfboard_template = pg.Surface((HALFBOARD_WIDTH, HALFBOARD_HEIGHT))
halfboard_template.fill(BOARD_BG)
pg.draw.rect(halfboard_template, BLACK, halfboard_template.get_rect(), LINE_WIDTH)

halfboard1 = halfboard_template.copy()
halfboard2 = halfboard_template.copy()

deck1_rv = [BOARD_MARGIN + HALFBOARD_WIDTH - ZONE_SIZE[0], ROW5, ZONE_SIZE[0], ZONE_SIZE[1]]
deck2_rv = [BOARD_MARGIN, ROW2, ZONE_SIZE[0], ZONE_SIZE[1]]
deck_template = pg.Surface((ZONE_SIZE[0], ZONE_SIZE[1]))
deck_template.fill(WHITE)
pg.draw.rect(deck_template, BLACK, deck_template.get_rect(), LINE_WIDTH)

deck1 = deck_template.copy()
deck2 = deck_template.copy()

gy1_rv = [BOARD_MARGIN + HALFBOARD_WIDTH - ZONE_SIZE[0], ROW4, ZONE_SIZE[0], ZONE_SIZE[1]]
gy2_rv = [BOARD_MARGIN, ROW3, ZONE_SIZE[0], ZONE_SIZE[1]]
gy_template = pg.Surface((ZONE_SIZE[0], ZONE_SIZE[1]))
gy_template.fill(GY_BG)
pg.draw.rect(gy_template, BLACK, gy_template.get_rect(), LINE_WIDTH)

gy1 = gy_template.copy()
gy2 = gy_template.copy()

mz1_rv = [BOARD_MARGIN + HALFBOARD_WIDTH/2 - ZONE_SIZE[0]/2, ROW4, ZONE_SIZE[0], ZONE_SIZE[1]]
mz2_rv = [BOARD_MARGIN + HALFBOARD_WIDTH/2 - ZONE_SIZE[0]/2, ROW3, ZONE_SIZE[0], ZONE_SIZE[1]]
mz_template = pg.Surface((ZONE_SIZE[0], ZONE_SIZE[1]))
mz_template.fill(WHITE)
pg.draw.rect(mz_template, BLACK, mz_template.get_rect(), LINE_WIDTH)

mz1 = mz_template.copy()
mz2 = mz_template.copy()


sz1_pos = [BOARD_MARGIN + HALFBOARD_WIDTH//2, ROW5]
sz2_pos = [BOARD_MARGIN + HALFBOARD_WIDTH//2, ROW2]
sz_template = pg.Surface((ZONE_SIZE[0], ZONE_SIZE[1]))
sz_template.fill(WHITE)
pg.draw.rect(sz_template, BLACK, sz_template.get_rect(), LINE_WIDTH)

row1_rv = [BOARD_MARGIN + ZONE_SIZE[0], ROW5, HALFBOARD_WIDTH - 2*ZONE_SIZE[0], ROW_HEIGHT - LINE_WIDTH]
row2_rv = [BOARD_MARGIN + ZONE_SIZE[0], ROW2 + LINE_WIDTH, HALFBOARD_WIDTH - 2*ZONE_SIZE[0], ROW_HEIGHT - LINE_WIDTH]
row1 = pg.Surface((HALFBOARD_WIDTH - 2*ZONE_SIZE[0], ROW_HEIGHT - LINE_WIDTH), pg.SRCALPHA)
for x in range(HALFBOARD_WIDTH - 2*ZONE_SIZE[0]):
    d = abs(x - (HALFBOARD_WIDTH - 2*ZONE_SIZE[0])/2)
    transparancy = 1 - d/(HALFBOARD_WIDTH - 2*ZONE_SIZE[0])*2
    pg.draw.line(row1, (200, 200, 250, 255*transparancy), (x, 0), (x, ROW_HEIGHT - LINE_WIDTH))

row2 = row1.copy()

hand1_center = [BOARD_MARGIN + HALFBOARD_WIDTH//2 - ZONE_SIZE[0]//2, ROW6]
hand2_center = [BOARD_MARGIN + HALFBOARD_WIDTH//2 - ZONE_SIZE[0]//2, ROW1]

title_pos = (WIDTH - RIGHT_MARGINE + 20, 30)
exp_pos = (title_pos[0] + 200, 100)
img_pos = (title_pos[0], 100)

END_BUTTON_SIZE = (200, 100)
end_button_rv = [WIDTH - END_BUTTON_SIZE[0] - 50, HEIGHT - END_BUTTON_SIZE[1] - 50, END_BUTTON_SIZE[0], END_BUTTON_SIZE[1]]
end_button = pg.Surface(END_BUTTON_SIZE)
end_button.fill(GY_BG)

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
    'row2': None,
    'endbutton': None
    }

player1 = TCG.HalfBoard('player 1')
player2 = TCG.HalfBoard('player 2')
game = TCG.Board(player1, player2)

cardlist = []

ref_dict = {
    'deck1': player1.deck,
    'deck2': player2.deck,
    'mainzone1': player1.main_zone,
    'mainzone2': player2.main_zone,
    'gy1': player1.graveyard,
    'gy2': player2.graveyard,
    'hand1': player1.hand,
    'hand2': player2.hand
    }

def get_key_priority(keys:list[str]):
    priority_order = [
        'mainzone',
        'gy',
        'deck',
        'temp zone',
        'row',
        'halfboard',
        'board'
    ]
    for key in keys:
        if 'subzone' not in key:
            basic = False
            for basic_key in priority_order:
                if basic_key in key:
                    basic = True
                    break
            if not basic:
                return key, 'card'
        elif 'subzone' in key:
            return key, 'comp'
    for basic_key in priority_order:
        if basic_key in key:
            return key, 'comp'
    return None, 'None'

hovering = []
clicking = []
unclicking = []
dragging = False
drag_from = None
making_subzone = 0

def screen_generator():
    def board_generator():
        gamecomponents.clear()
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
        gamecomponents['endbutton'] = SURF.blit(end_button, end_button_rv)

    def subzone_generator():
        subzone_tot = len(game.player1.row.subzones) + bool(making_subzone)
        if subzone_tot > 0:
            for subzone_num in range(subzone_tot):
                pos = (
                    sz1_pos[0] + (subzone_num - subzone_tot/2)*ZONE_SIZE[0] + (subzone_num - (subzone_tot - 1)/2)*SUBZONE_MARGIN,
                    sz1_pos[1]
                    )
                if (making_subzone - 1) == subzone_num:
                    gamecomponents['temp zone'] = SURF.blit(sz_template, pos)
                    ref_dict['temp zone'] = 'temp zone'
                else:
                    subzone_index = subzone_num - bool(-1 < making_subzone - 1 < subzone_num)
                    gamecomponents[f'subzone1-{subzone_index}'] = SURF.blit(sz_template, pos)
                    ref_dict[f'subzone1-{subzone_index}'] = game.player1.row.subzones[subzone_index]

    def card_generator():
        for card in range(len(ref_dict['deck1'].cards)):
            SURF.blit(card_back_image, (card_on_zone(deck1_rv)[0], card_on_zone(deck1_rv)[1] + 4*card))
        for card in range(len(ref_dict['mainzone1'].cards)):
            SURF.blit(card_back_image, (card_on_zone(mz1_rv)[0], card_on_zone(mz1_rv)[1] + 4*card))
        for card in range(len(ref_dict['gy1'].cards)):
            SURF.blit(card_back_image, (card_on_zone(gy1_rv)[0], card_on_zone(gy1_rv)[1] + 4*card))
        for card in range(len(ref_dict['hand1'].cards)):
            SURF.blit(card_back_image, (card_on_zone(hand1_center)[0] - len(ref_dict['hand1'].cards) + card, card_on_zone(hand1_center)[1]))
        for card in range(len(ref_dict['hand2'].cards)):
            pass
        for subzone in [key for key in gamecomponents if 'subzone' in key]:
            for card in range(len(ref_dict[subzone].cards)):
                SURF.blit(card_back_image, (gamecomponents[subzone].x + ZONE_MARGIN, gamecomponents[subzone].y + ZONE_MARGIN + 4*card))
        if dragging:
            gamecomponents['sample card'] = SURF.blit(
                card_back_image, tuple(sum(elem) for elem in zip(pg.mouse.get_pos(), (-50, -70)))
                )
        elif not dragging and 'sample card' in gamecomponents:
            del gamecomponents['sample card']

    def explanation_generator():
        explanation = ['', '', None]

        def get_card_explanation(cardcomponent):
            title = 'Sample Card'
            explanation = 'A dummy card for test.'
            img = card_back_image
            return [title, explanation, img]

        def get_gamecomponent_explanation(key):
            title = None
            explanation = None
            img = None
            if key == None:
                pass
            elif key == 'board':
                title = 'Board'
                explanation = 'Where game is played.'
            elif key == 'halfboard1':
                title = 'Your Halfboard'
                explanation = 'Your side of the board.'
            elif key == 'halfboard2':
                title = "Opponent's Halfboard"
                explanation = "The opponent's side of the board"
            elif key == 'deck1':
                title = 'Your Deck'
                explanation = 'Your Deck.'
            elif key == 'row1':
                title = 'Your Row'
                explanation = 'Place here to make a new Sub Zone.'
            elif key == 'mainzone1':
                title = 'Main Zone'
                explanation = 'Place here to end turn.'
            elif key == 'gy1':
                title = 'Your Graveyard'
                explanation = 'Used cards are here.'
            elif 'subzone1-' in key:
                title = f'Your Sub Zone {key[9:]}'
                explanation = 'Your Sub Zone.'
            elif key == 'temp zone':
                title = f'New Sub Zone'
                explanation = 'Place card here to create new Sub Zone.'
            return [title, explanation, img]

        if dragging:
            if len(hovering) == 1:
                explanation = get_card_explanation(hovering[0])
            else:
                key, str = get_key_priority(hovering[:-1])
                explanation = get_card_explanation(key) if str == 'card' else get_gamecomponent_explanation(key)
        elif hovering != []:
            key, str = get_key_priority(hovering)
            explanation = get_card_explanation(key) if str == 'card' else get_gamecomponent_explanation(key)
        else:
            explanation = ['No hovering', '', None]

        rendered_title = TITLE_FONT.render(explanation[0], True, BLACK)
        rendered_explanation = EXP_FONT.render(explanation[1], True, BLACK)
        rendered_img = pg.transform.scale(explanation[2], (180, 240)) if explanation[2] != None else None

        SURF.blit(rendered_title, title_pos)
        SURF.blit(rendered_explanation, exp_pos)
        if rendered_img:
            SURF.blit(rendered_img, img_pos)


    SURF.fill(WHITE)

    board_generator()
    subzone_generator()
    card_generator()
    explanation_generator()

gameplay = game.play()
next(gameplay)

def calculate(message):
    re = gameplay.send(message)
    next(gameplay)
    return re

screen_generator()

REFRESH = True

while REFRESH:
    frame_clicking = []
    unclicking = []
    for event in pg.event.get():
        if event.type == pg.QUIT:
            REFRESH = False
            continue

        if event.type == pg.MOUSEMOTION:
            #print('moved')
            hovering = []
            for key in gamecomponents:
                if gamecomponents[key].collidepoint(pg.mouse.get_pos()):
                    print(f'you are on {key}.')
                    hovering.append(key)
            if dragging:
                if len(hovering) > 1 and 'row1' in hovering and not any('subzone1' in s for s in hovering):
                    subzone_x = []
                    for subzone in [key for key in gamecomponents if 'subzone1' in key]:
                        subzone_x.append(gamecomponents[subzone].x)
                    subzone_x.sort()
                    x = pg.mouse.get_pos()[0]
                    for i in range(len(subzone_x)):
                        if subzone_x[i] > x:
                            making_subzone = i + 1
                            break
                    if making_subzone == 0:
                        making_subzone = len(subzone_x) + 1
                else:
                    making_subzone = 0

        if event.type == pg.MOUSEBUTTONDOWN:
            print('pressed')
            for key in gamecomponents:
                if gamecomponents[key].collidepoint(pg.mouse.get_pos()):
                    print(f'you clicked {key}.')
                    #frame_clicking.append(key)
                    for place in ['deck1', 'deck2', 'mainzone1', 'mainzone2', 'gy1', 'gy2']:
                        if place == key and len(ref_dict[key].cards) > 0 and not dragging:
                            dragging = True
                            drag_from = key
                            calculate(['click', ref_dict[key]])

        if event.type == pg.MOUSEBUTTONUP:
            print('unpressed')
            for key in gamecomponents:
                if gamecomponents[key].collidepoint(pg.mouse.get_pos()):
                    print(f'you unclicked {key}.')
                    #frame_unclicking.append(key)
                    if dragging:
                        for component in ['gy1', 'gy2']:
                            if key == component:
                                ref_dict[key].cards.append(len(ref_dict[key].cards))
                                unclicking.append([dragging, key])
                                dragging = False
                        if key in ['mainzone1','temp zone'] or 'subzone1' in key:
                            if calculate(['drop', ref_dict[key], dragging, making_subzone]) != True:
                                print('Subzone Error')
                            dragging = False
                    
                    elif key == 'endbutton':
                        if calculate(['drop', 'end']) != True:
                            print('Turn error!')
                            
            if dragging:
                ref_dict[drag_from].cards.append(len(ref_dict[drag_from].cards))
            dragging = False
            drag_from = None
            making_subzone = 0

    screen_generator()
    pg.display.update()

pg.quit()
sys.exit()