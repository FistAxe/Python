import pygame as pg
import sys
import os
from typing import Union, Literal

root_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(root_dir)
import TCG
import TCGplayer

pg.init()

# region Screen Size
WIDTH = 1280
HEIGHT = 768
# endregion

# region Color
WHITE = pg.Color(255, 255, 255)
BLACK = pg.Color(0, 0, 0)
DARK_BLUE = pg.Color(50, 50, 100)
DARK_RED = pg.Color(100, 50, 50)
BOARD_BG = pg.Color(230, 230, 255)
ROW_BG = pg.Color(200, 200, 255)
GY_BG = pg.Color(200, 200, 200)

MANA_R = pg.Color(255, 50, 50)
MANA_Y = pg.Color(200, 200, 50)
MANA_B = pg.Color(50, 50, 255)
# endregion

# Screen Init
SURF = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption('TCG')
SURF.fill(WHITE)

FPS = pg.time.Clock()
FPS.tick(60)

# region Layout
RIGHT_MARGINE = 500
BOARD_MARGIN = 5
BOARD_WIDTH = WIDTH - RIGHT_MARGINE - 2*BOARD_MARGIN
LINE_WIDTH = 3
CARD_SIZE = (75, 105)

COLUMN_WIDTH = CARD_SIZE[0] + 10
ROW_HEIGHT = CARD_SIZE[1] + 10
COLUMN_SPACING = 10

ROW_MIDDLE = HEIGHT//2
ROW_SPACING = 20
ROW_UP = ROW_MIDDLE - ROW_HEIGHT - ROW_SPACING
ROW_DOWN = ROW_MIDDLE + ROW_HEIGHT + ROW_SPACING

COLUMN_LEFT = BOARD_MARGIN + COLUMN_WIDTH//2
COLUMN_RIGHT = BOARD_MARGIN + BOARD_WIDTH - COLUMN_WIDTH//2
# endregion

# region Card
CARD_NAME_HEIGHT = 12
card_back_image = pg.image.load(os.path.join(root_dir, 'images', 'card_back.png')).convert()
card_front_image = pg.image.load(os.path.join(root_dir, 'images', 'card_front.png')).convert()
card_front_R = pg.image.load(os.path.join(root_dir, 'images', 'card_front_R.png')).convert()
card_front_Y = pg.image.load(os.path.join(root_dir, 'images', 'card_front_Y.png')).convert()
card_front_B = pg.image.load(os.path.join(root_dir, 'images', 'card_front_B.png')).convert()
card_active_border = pg.image.load(os.path.join(root_dir, 'images', 'card_active_border.png')).convert_alpha()

card_back_active = card_back_image.copy()
card_front_active = card_front_image.copy()
card_front_R_active = card_front_R.copy()
card_front_Y_active = card_front_Y.copy()
card_front_B_active = card_front_B.copy()
for card in [card_back_active, card_front_active, card_front_R_active, card_front_Y_active, card_front_B_active]:
    card.blit(card_active_border, (0, 0))

# Card Fonts
NAME_FONT = pg.font.SysFont('Gulim', 11)
POWER_FONT = pg.font.SysFont('Segoe UI Black', 16, italic=True)
SPEED_FONT = pg.font.SysFont('Verdana', 13, bold=True)
NAME_COORD = (14, 1)
IMAGE_COORD = (2, 13)
POWER_COORD = (4, CARD_SIZE[1] - 20)
SPEED_COORD = (4, CARD_SIZE[1] - 40)
power_dict: dict[int, pg.Surface] = {}
speed_dict: dict[int, pg.Surface] = {}
speed_dict[1] = SPEED_FONT.render('I', False, BLACK)
speed_dict[2] = SPEED_FONT.render('II', False, BLACK)
speed_dict[3] = SPEED_FONT.render('III', False, BLACK)
speed_dict[4] = SPEED_FONT.render('IV', False, BLACK)
speed_dict[5] = SPEED_FONT.render('V', False, BLACK)
speed_dict[6] = SPEED_FONT.render('VI', False, BLACK)
speed_dict[7] = SPEED_FONT.render('VII', False, BLACK)
speed_dict[8] = SPEED_FONT.render('VIII', False, BLACK)
speed_dict[9] = SPEED_FONT.render('IX', False, BLACK)
speed_dict[10] = SPEED_FONT.render('X', False, BLACK)
# endregion

def get_power_image(power:int):
    if power not in power_dict:
        power_dict[power] = POWER_FONT.render(str(power), False, BLACK)
    return power_dict[power]

def get_speed_image(speed:int):
    if speed not in speed_dict:
        speed_dict[speed] = SPEED_FONT.render(str(speed), False, BLACK)
    return speed_dict[speed]

# region Zone
ZONE_MARGIN = 2
ZONE_SIZE = [CARD_SIZE[0] + 2*ZONE_MARGIN, CARD_SIZE[1] + 2*ZONE_MARGIN]
# endregion

def get_card_rv(zone_topleft_pos):
    '''zone topleft pos -> rv (topleft)'''
    return [zone_topleft_pos[0] + ZONE_MARGIN, zone_topleft_pos[1] + ZONE_MARGIN]

def topleft(*rv:int):
    return (rv[0] - COLUMN_WIDTH//2, rv[1] - ROW_HEIGHT//2)

# region Board
# rv is topleft!
deck1_rv = topleft(COLUMN_RIGHT, ROW_DOWN)
deck2_rv = topleft(COLUMN_LEFT, ROW_UP)
deck_surface = pg.Surface(ZONE_SIZE)
deck_surface.fill(WHITE)
pg.draw.rect(deck_surface, BLACK, deck_surface.get_rect(), LINE_WIDTH)

gy1_rv = topleft(COLUMN_RIGHT, ROW_MIDDLE)
gy2_rv = topleft(COLUMN_LEFT, ROW_MIDDLE)
graveyard_surface = pg.Surface(ZONE_SIZE)
graveyard_surface.fill(GY_BG)
pg.draw.rect(graveyard_surface, BLACK, graveyard_surface.get_rect(), LINE_WIDTH)

row_rv = (BOARD_MARGIN + COLUMN_WIDTH, HEIGHT//2 - ROW_HEIGHT//2)
row_surface = pg.Surface((BOARD_WIDTH - 2*COLUMN_WIDTH, ROW_HEIGHT), pg.SRCALPHA)
for x in range(BOARD_WIDTH - 2*COLUMN_WIDTH):
    d = abs(x - (BOARD_WIDTH - 2*COLUMN_WIDTH)/2)
    transparancy = 1 - d/(BOARD_WIDTH - 2*ZONE_SIZE[0])*2
    pg.draw.line(row_surface, (200, 200, 250, int(255*transparancy)), (x, 0), (x, ROW_HEIGHT - LINE_WIDTH))

column_surface = pg.Surface((COLUMN_WIDTH, 2*ROW_HEIGHT), pg.SRCALPHA)

hand_img = pg.Surface((BOARD_WIDTH, ROW_HEIGHT))
hand_img.fill(WHITE)
hand1_center = (BOARD_MARGIN + BOARD_WIDTH//2, BOARD_MARGIN + ROW_HEIGHT//2)
hand2_center = (BOARD_MARGIN + BOARD_WIDTH//2, HEIGHT - ROW_HEIGHT//2 - BOARD_MARGIN)
hand1_rv = (hand1_center[0] - BOARD_WIDTH//2, hand1_center[1] - ROW_HEIGHT//2)
hand2_rv = (hand2_center[0] - BOARD_WIDTH//2, hand2_center[1] - ROW_HEIGHT//2)
# endregion

# region Explanation
TITLE_FONT = pg.font.SysFont('Gulim', 40)
EXP_FONT = pg.font.SysFont('Gulim', 15)

title_pos = (WIDTH - RIGHT_MARGINE + 20, 30)
exp_pos = (title_pos[0] + 200, 100)
img_pos = (title_pos[0], 100)
# endregion

background = pg.Surface((WIDTH, HEIGHT))
background.fill(WHITE)
background.blits((
    (deck_surface, deck1_rv),
    (deck_surface, deck2_rv),
    (graveyard_surface, gy1_rv),
    (graveyard_surface, gy2_rv),
    (row_surface, row_rv)
))
background = background.convert()

# real images on the board. May be different from real data.
rects : dict[TCG.GameComponent, pg.Rect] = {}

player1 = TCGplayer.player1
player2 = TCGplayer.player2
game = TCG.Game(player1, player2)

card_image_dict: dict[type[TCG.Card], pg.Surface] = {}
card_image_active_dict: dict[type[TCG.Card], pg.Surface] = {}
choice_image_dict: dict[str, pg.Surface] = {}
choice_image_dict['default'] = pg.image.load(os.path.join(root_dir, 'images', 'choice_default.png')).convert_alpha()
choice_image_dict['attack'] = pg.image.load(os.path.join(root_dir, 'images', 'choice_attack.png')).convert_alpha()

hovering = set()
holding = None
choices : list[TCG.Choice] = []

rects = {}
rects[game.deck[player1]] = pg.Rect(deck1_rv, ZONE_SIZE)
rects[game.deck[player2]] = pg.Rect(deck2_rv, ZONE_SIZE)
rects[game.graveyard[player1]] = pg.Rect(gy1_rv, ZONE_SIZE)
rects[game.graveyard[player2]] = pg.Rect(gy2_rv, ZONE_SIZE)

def get_colliding_rect_keys():
    return {key for key in rects if rects[key].collidepoint(pg.mouse.get_pos()) and key is not holding}

def get_card_image(card:TCG.Card):
    covered_type = card.covered_type()
    if covered_type in ('half', 'none') or (covered_type == 'hidden' and card.owner is game.current_player):
        # Use premade image for background
        if type(card) not in card_image_dict:
            # Make one.
            if card.color == 'R':
                real_image_bg = card_front_R.copy()
                real_image_active_bg = card_front_R_active.copy()
            elif card.color == 'Y':
                real_image_bg = card_front_Y.copy()
                real_image_active_bg = card_front_Y_active.copy()
            elif card.color == 'B':
                real_image_bg = card_front_B.copy()
                real_image_active_bg = card_front_B_active.copy()
            else:
                real_image_bg = card_front_image.copy()
                real_image_active_bg = card_front_active.copy()
            
            if card.image:
                img = pg.image.load(card.image).convert()
                real_image_bg.blit(img, IMAGE_COORD)
                real_image_active_bg.blit(img, IMAGE_COORD)
            if card.name:
                name = NAME_FONT.render(card.name, False, BLACK)
                real_image_bg.blit(name, NAME_COORD)
                real_image_active_bg.blit(img, NAME_COORD)

            card_image_dict[type(card)] = real_image_bg.convert()
            card_image_active_dict[type(card)] = real_image_active_bg.convert()

        real_image = card_image_dict[type(card)] if not any((effect in choices) for effect in card.effects) else card_image_active_dict[type(card)]

        # Draw variable values on each frame
        if card.power:
            real_image.blit(get_power_image(card.power), POWER_COORD)
        
        return real_image
    else:
        return card_back_active if not any((effect in choices) for effect in card.effects) else card_back_image

def get_hovering_priority() -> TCG.GameComponent|None:
    global hovering, holding
    priority_order = [
        TCG.Deck,
        TCG.Card,
        TCG.Graveyard,
        TCG.Column
    ]
        
    cards = [key for key in hovering if isinstance(key, TCG.Card) and key != holding]
    if cards:
        return cards.pop()
    
    for type in priority_order:
        for key in hovering:
            if isinstance(key, type):
                return key
    
    return None

def get_key(drag:bool):
    global holding
    source_target = 'source' if drag else 'target'
    keys = get_colliding_rect_keys() & {choice[source_target] for choice in choices}
    cards = {key for key in keys if isinstance(key, TCG.Card)}
    piles = {key for key in keys if isinstance(key, TCG.Pile)}
    key : TCG.GameComponent|None = None

    if cards:
        piles_of_cards = {card.location for card in cards if card.location}
        if len(piles_of_cards) > 1:
            raise Exception('Selected Two Cards at Once!')
        elif len(piles_of_cards) == 0:
            pass
        else:
            pile = piles_of_cards.pop()
            if isinstance(pile, TCG.Deck):
                pass
            else:
                for card in reversed(pile.cards):
                    if card in cards:
                        key = card
    elif len(piles) == 1:
        key = piles.pop()
    else:
        key = None
    
    holding = key if drag else None
    return key

def screen_generator():
    def _column_generator():
        def get_column_rv(column:TCG.Column):
            length = len(game.row.columns)
            index = game.row.columns.index(column)
            return (BOARD_MARGIN + BOARD_WIDTH//2 + (index - (length + COLUMN_SPACING)/2)*COLUMN_WIDTH,
                    ROW_MIDDLE - ROW_HEIGHT//2)
        
        for column in game.row.columns:
            rects[column] = SURF.blit(column_surface, get_column_rv(column))
    
    def _card_generator(card:TCG.Card, rv:list[int]|tuple[int, int], reversed:bool):
        '''rv: center!'''
        if card is holding:
            return False
        
        card_surface = get_card_image(card)

        if reversed:
            card_surface = pg.transform.flip(card_surface, True, True)
        
        rects[card] = SURF.blit(card_surface, get_card_rv(rv))
        return True
    
    def _pile_generator(pile:TCG.Pile, reversed=False, margin:int=4):
        rv = list(rects[pile].topleft)
        for card in pile.cards:
            if _card_generator(card, rv, reversed):
                rv[1] -= margin
    
    def _hand_generator(hand:TCG.Hand, reversed=False, margin:int = 20):
        rv = list(rects[hand].center)
        rv[0] -= (len(hand.cards) - 1)*margin
        for card in hand.cards:
            _card_generator(card, rv, reversed)
            rv[0] += margin

    def _explanation_generator():
        explanation = ['', '', None]

        def get_card_explanation(card:TCG.Card):
            title = card.name if card.name else 'Sample Card'
            discription = card.description if card.description else 'A dummy card for test.'
            img = get_card_image(card)
            return [title, discription, img]

        def get_gamecomponent_explanation(key:TCG.GameComponent):
            title = None
            discription = None
            img = None
            if key == None:
                pass
            elif key == game.deck[game.current_player]:
                title = 'Your Deck'
                discription = 'Your Deck.'
            elif key == game.graveyard[game.current_player]:
                title = 'Your Graveyard'
                discription = 'Used cards are here.'
            return [title, discription, img]

        key = get_hovering_priority()
        if key:
            if isinstance(key, TCG.Card):
                explanation = get_card_explanation(key)
            else:
                explanation = get_gamecomponent_explanation(key)
        else:
            explanation = ['No hovering', '', None]

        rendered_title = TITLE_FONT.render(explanation[0], True, BLACK)
        rendered_explanation = EXP_FONT.render(explanation[1], True, BLACK)
        rendered_img = pg.transform.scale(explanation[2], (180, 240)) if explanation[2] != None else None

        SURF.blit(rendered_title, title_pos)
        SURF.blit(rendered_explanation, exp_pos)
        if rendered_img:
            SURF.blit(rendered_img, img_pos)

    SURF.blit(background, (0, 0))
    rects[game.hand[player1]] = SURF.blit(hand_img, hand1_rv, area=(0, 0, CARD_SIZE[0] + 20*(game.hand[player1].length - 1), ZONE_SIZE[1]))
    rects[game.hand[player2]] = SURF.blit(hand_img, hand2_rv, area=(0, 0, CARD_SIZE[0] + 20*game.hand[player2].length, ZONE_SIZE[1]))
    _column_generator()

    for pile in [game.deck[player2], game.graveyard[player2]]:
        _pile_generator(pile, reversed=True)

    for pile in [game.graveyard[player1], game.deck[player1]]:
        _pile_generator(pile, reversed=False)

    # HAND
    _hand_generator(game.hand[player1])
    _hand_generator(game.hand[player2], reversed=True)

    if isinstance(holding, TCG.Card):
        rects[holding] = SURF.blit(
            get_card_image(holding),
            tuple(sum(elem) for elem in zip(pg.mouse.get_pos(), (-50, -70)))
            )

    _explanation_generator()

# Start
gameplay = game.IO()
next(gameplay)
refresh = True
screen_generator()

def calculate(message:TCG.INPUTTYPE):
    global choices
    result = gameplay.send(message)
    if isinstance(result, str):
        choices = []
        print(result)    # Add Log Later!
    else:
        choices = result

try:
    while refresh:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                refresh = False
                continue

            if event.type == pg.MOUSEMOTION:
                # Initialize hovering (As you moved.)
                hovering = get_colliding_rect_keys()

            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 3:
                    calculate(TCG.CANCEL)
                elif not holding:
                    result = calculate(get_key(drag=True))
                else:
                    raise Exception('Tryed to click while dragging.')

            if event.type == pg.MOUSEBUTTONUP:
                if event.button == 3 or not holding:
                    pass
                else:
                    result = calculate(get_key(drag=False))

        screen_generator()
        pg.display.update()
except StopIteration as e:
    print(e.value)

SURF.fill(WHITE)
gameover_message = TITLE_FONT.render(f'{game.opponent(game.current_player).name} Survives!', True, BLACK)
SURF.blit(gameover_message, (SURF.get_width()//2 - gameover_message.get_width()//2,
                             SURF.get_height()//2 - gameover_message.get_height()//2))
pg.display.update()

watching = True
while watching:
    for event in pg.event.get():
        if event.type in [pg.QUIT, pg.MOUSEBUTTONDOWN]:
            watching = False

pg.quit()
sys.exit()