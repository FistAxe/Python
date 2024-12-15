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
board_img = pg.Surface((HALFBOARD_WIDTH, HALFBOARD_HEIGHT*2))
board_img.fill(WHITE)

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

hand_img = pg.Surface((10, 10))
hand_img.fill(WHITE)
hand1_center = [BOARD_MARGIN + HALFBOARD_WIDTH//2 - ZONE_SIZE[0]//2, ROW6]
hand2_center = [BOARD_MARGIN + HALFBOARD_WIDTH//2 - ZONE_SIZE[0]//2, ROW1]

title_pos = (WIDTH - RIGHT_MARGINE + 20, 30)
exp_pos = (title_pos[0] + 200, 100)
img_pos = (title_pos[0], 100)

END_BUTTON_SIZE = (200, 100)
end_button_rv = [WIDTH - END_BUTTON_SIZE[0] - 50, HEIGHT - END_BUTTON_SIZE[1] - 50, END_BUTTON_SIZE[0], END_BUTTON_SIZE[1]]
end_button = pg.Surface(END_BUTTON_SIZE)
end_button.fill(GY_BG)

# real images on the board. May be different from real data.
gamecomponents: dict[TCG.Board|TCG.Pack|TCG.Card|TCG.Row|str, pg.Rect] = {}

player1 = TCG.HalfBoard('player 1')
player2 = TCG.HalfBoard('player 2')
board = TCG.Board(player1, player2)

cardlist = []

def get_key_priority(keys:list[str]):
    priority_order = [
        TCG.MainZone,
        TCG.Graveyard,
        TCG.Deck,
        TCG.Row,
        TCG.HalfBoard,
        TCG.Board
    ]
    if 'temp zone' in keys:
        return 'temp zone', 'comp'
    else:
        for type in priority_order:
            for key in keys:
                if isinstance(key, type):
                    return key, 'comp'
    return None, 'None'

hovering = []
clicking = []
unclicking = []
making_subzone = 0

def screen_generator():
    def board_generator():
        global gamecomponents
        gamecomponents = {}
        gamecomponents[board] = SURF.blit(board_img, board_rv)
        gamecomponents[player1] = SURF.blit(halfboard1, half1_rv)
        gamecomponents[player2] = SURF.blit(halfboard2, half2_rv)
        gamecomponents[player1.deck] = SURF.blit(deck1, deck1_rv)
        gamecomponents[player2.deck] = SURF.blit(deck2, deck2_rv)
        gamecomponents[player1.graveyard] = SURF.blit(gy1, gy1_rv)
        gamecomponents[player2.graveyard] = SURF.blit(gy2, gy2_rv)
        gamecomponents[player1.main_zone] = SURF.blit(mz1, mz1_rv)
        gamecomponents[player2.main_zone] = SURF.blit(mz2, mz2_rv)
        gamecomponents[player1.row] = SURF.blit(row1, row1_rv)
        gamecomponents[player2.row] = SURF.blit(row2, row2_rv)
        gamecomponents[player1.hand] = SURF.blit(hand_img, hand1_center)
        gamecomponents[player2.hand] = SURF.blit(hand_img, hand2_center)
        gamecomponents['endbutton'] = SURF.blit(end_button, end_button_rv)

    def subzone_generator():
        subzone_tot = len(board.player1.row.subzones) + bool(making_subzone)
        if subzone_tot > 0:
            for subzone_num in range(subzone_tot):
                pos = (
                    sz1_pos[0] + (subzone_num - subzone_tot/2)*ZONE_SIZE[0] + (subzone_num - (subzone_tot - 1)/2)*SUBZONE_MARGIN,
                    sz1_pos[1]
                    )
                if (making_subzone - 1) == subzone_num:
                    gamecomponents['temp zone'] = SURF.blit(sz_template, pos)
                else:
                    subzone_index = subzone_num - bool(-1 < making_subzone - 1 < subzone_num)
                    gamecomponents[player1.row.subzones[subzone_index]] = SURF.blit(sz_template, pos)

    def card_generator():
        cards_shown_dict: dict[str, list] = {}
        for key in gamecomponents:
            # Ignore cardlist generation on temp zone
            if isinstance(key, TCG.Pack) or isinstance(key, TCG.Hand):
                cards_shown_dict[key] = key.cards.copy()
        # Holding card is not shown on its place
        if board.holding_from in cards_shown_dict:
            cards_shown_dict[board.holding_from].pop()

        # ROW5
        for subzone in [key for key in gamecomponents if isinstance(key, TCG.SubZone)]:
            for i, card in enumerate(cards_shown_dict[subzone]):
                gamecomponents[card] = SURF.blit(card_back_image,
                                                 (gamecomponents[subzone].x + ZONE_MARGIN, gamecomponents[subzone].y + ZONE_MARGIN + 4*i)
                                                 )
        for i, card in enumerate(cards_shown_dict[player1.deck]):
            gamecomponents[card] = SURF.blit(card_back_image, (card_on_zone(deck1_rv)[0], card_on_zone(deck1_rv)[1] + 4*i))
        # ROW4
        for i, card in enumerate(cards_shown_dict[player1.main_zone]):
            gamecomponents[card] = SURF.blit(card_back_image, (card_on_zone(mz1_rv)[0], card_on_zone(mz1_rv)[1] + 4*i))
        for i, card in enumerate(cards_shown_dict[player1.graveyard]):
            gamecomponents[card] = SURF.blit(card_back_image, (card_on_zone(gy1_rv)[0], card_on_zone(gy1_rv)[1] + 4*i))
        # HAND
        for i, card in enumerate(cards_shown_dict[player1.hand]):
            gamecomponents[card] = SURF.blit(card_back_image,
                                             (card_on_zone(hand1_center)[0] - len(cards_shown_dict[player1.hand]) + i*20, card_on_zone(hand1_center)[1])
                                             )
        for i, card in enumerate(cards_shown_dict[player2.hand]):
            gamecomponents[card] = SURF.blit(card_back_image,
                                             (card_on_zone(hand2_center)[0] - len(cards_shown_dict[player2.hand]) + i*20, card_on_zone(hand2_center)[1])
                                             )

        if board.holding:
            gamecomponents[board.holding] = SURF.blit(
                card_back_image, tuple(sum(elem) for elem in zip(pg.mouse.get_pos(), (-50, -70)))
                )
        elif not board.holding and 'sample card' in gamecomponents:
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
            elif isinstance(key, TCG.Board):
                title = 'Board'
                explanation = 'Where game is played.'
            elif key == player1:
                title = 'Your Halfboard'
                explanation = 'Your side of the board.'
            elif key == player2:
                title = "Opponent's Halfboard"
                explanation = "The opponent's side of the board"
            elif key == player1.deck:
                title = 'Your Deck'
                explanation = 'Your Deck.'
            elif key == player1.row:
                title = 'Your Row'
                explanation = 'Place here to make a new Sub Zone.'
            elif key == player1.main_zone:
                title = 'Main Zone'
                explanation = 'Place here to end turn.'
            elif key == player1.graveyard:
                title = 'Your Graveyard'
                explanation = 'Used cards are here.'
            elif isinstance(key, TCG.SubZone):
                title = f'Your Sub Zone {key.name}'
                explanation = 'Your Sub Zone.'
            elif key == 'temp zone':
                title = f'New Sub Zone'
                explanation = 'Place card here to create new Sub Zone.'
            return [title, explanation, img]

        if board.holding:
            # On nowhere -> Show card itself
            if len(hovering) == 1:
                explanation = get_card_explanation(hovering[0])
            # On place -> Show place information
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

gameplay = board.play()
next(gameplay)

def calculate(message):
    re = gameplay.send(message)
    if type(re) == str:
        REFRESH = False
        raise Exception(f'Exception {re} occured.')
    else:
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
            # Initialize hovering (As you moved.)
            hovering = []
            for key in gamecomponents:
                if gamecomponents[key].collidepoint(pg.mouse.get_pos()):
                    print(f'you are on {key}.')
                    hovering.append(key)
            
            # Below is only for subzone indexing.
            if board.holding:
                # Trying to make subzone.
                if any(isinstance(comp, TCG.Row) for comp in hovering) and not any(isinstance(comp, TCG.SubZone) for comp in hovering):
                    subzone_x = []
                    for subzone in player1.row.subzones:
                        subzone_x.append(gamecomponents[subzone].x)
                    subzone_x.sort()
                    x = pg.mouse.get_pos()[0]
                    for i in range(len(subzone_x)):
                        # There is more than 1 existing subzone on left
                        if subzone_x[i] > x:
                            making_subzone = i + 1
                            break
                    # Making subzone on very left
                    if making_subzone == 0:
                        making_subzone = len(subzone_x) + 1
                # Giving up making subzone.
                else:
                    making_subzone = 0

        if event.type == pg.MOUSEBUTTONDOWN:
            # print('pressed')
            if not board.holding:
                keys = []
                for key in gamecomponents:
                    if gamecomponents[key].collidepoint(pg.mouse.get_pos()):
                        print(f'you clicked {key}.')
                        keys.append(key)
                calculate(['click', keys])
            else:
                raise Exception('Tryed to click while dragging.')

        if event.type == pg.MOUSEBUTTONUP:
            print('unpressed')
            keys = []
            for key in gamecomponents:
                if gamecomponents[key].collidepoint(pg.mouse.get_pos()):
                    print(f'you unclicked {key}.')
                    keys.append(key)
            if board.holding:
                ans = calculate(['drop', keys, making_subzone])
                if ans == False:
                    raise Exception('Something went Wrong')
                elif isinstance(ans, str):
                    raise Exception(ans)
            making_subzone = 0

    screen_generator()
    pg.display.update()

pg.quit()
sys.exit()