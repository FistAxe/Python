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
LINE_WIDTH = 3
INDICATOR_HEIGHT = 40
HALFBOARD_WIDTH = WIDTH - RIGHT_MARGINE - 2*BOARD_MARGIN
ROW_HEIGHT = (HEIGHT - 2*BOARD_MARGIN - INDICATOR_HEIGHT)//6
HALFBOARD_HEIGHT = ROW_HEIGHT*2

ROW1 = BOARD_MARGIN
ROW2 = ROW1 + ROW_HEIGHT
ROW3 = ROW2 + ROW_HEIGHT
ROW_I = ROW3 + ROW_HEIGHT
ROW4 = ROW_I + INDICATOR_HEIGHT
ROW5 = ROW4 + ROW_HEIGHT
ROW6 = ROW5 + ROW_HEIGHT
# endregion

# region Card
CARD_SIZE = [75, 105]
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
SUBZONE_MARGIN = 40
ZONE_HEIGHT_FIX = (ROW_HEIGHT - ZONE_SIZE[1])//2
if ZONE_HEIGHT_FIX < 0:
    ZONE_HEIGHT_FIX = 0
# endregion

def card_on_zone(zone_center_pos, is_turned:bool=False):
    '''zone center pos -> rv (topleft)'''
    if is_turned:
        return [zone_center_pos[0] - CARD_SIZE[1]//2, zone_center_pos[1] - CARD_SIZE[0]//2]
    else:
        return [zone_center_pos[0] - CARD_SIZE[0]//2, zone_center_pos[1] - CARD_SIZE[1]//2]

# region Column
ROW_WIDTH = HALFBOARD_WIDTH - ZONE_SIZE[0]*2
MARGINE_BETWEEN_ZONES = 60
COLUMN_LEFT = BOARD_MARGIN
COLUMN1 = COLUMN_LEFT + ZONE_SIZE[0] + ROW_WIDTH//2 - ZONE_SIZE[0]//2 - MARGINE_BETWEEN_ZONES - ZONE_SIZE[0]
COLUMN2 = COLUMN_LEFT + ZONE_SIZE[0] + ROW_WIDTH//2 - ZONE_SIZE[0]//2
COLUMN3 = COLUMN_LEFT + ZONE_SIZE[0] + ROW_WIDTH//2 + ZONE_SIZE[0]//2 + MARGINE_BETWEEN_ZONES
COLUMN_RIGHT = COLUMN_LEFT + ZONE_SIZE[0] + ROW_WIDTH
# endregion

def get_zonetyp_rv(left:int, top:int):
    return [left, top + ZONE_HEIGHT_FIX, ZONE_SIZE[0], ZONE_SIZE[1]]

# region Board
board_rv = [BOARD_MARGIN, ROW2, HALFBOARD_WIDTH, HALFBOARD_HEIGHT*2]
board_surface = pg.Surface((HALFBOARD_WIDTH, HALFBOARD_HEIGHT*2))
board_surface.fill(WHITE)

half1_rv = [BOARD_MARGIN, ROW4, HALFBOARD_WIDTH, HALFBOARD_HEIGHT]
half2_rv = [BOARD_MARGIN, ROW2, HALFBOARD_WIDTH, HALFBOARD_HEIGHT]
halfboard_surface = pg.Surface((HALFBOARD_WIDTH, HALFBOARD_HEIGHT))
halfboard_surface.fill(BOARD_BG)
pg.draw.rect(halfboard_surface, BLACK, halfboard_surface.get_rect(), LINE_WIDTH)

deck1_rv = get_zonetyp_rv(COLUMN_RIGHT, ROW5)
deck2_rv = get_zonetyp_rv(COLUMN_LEFT, ROW2)
deck_surface = pg.Surface(ZONE_SIZE)
deck_surface.fill(WHITE)
pg.draw.rect(deck_surface, BLACK, deck_surface.get_rect(), LINE_WIDTH)

gy1_rv = get_zonetyp_rv(COLUMN_RIGHT, ROW4)
gy2_rv = get_zonetyp_rv(COLUMN_LEFT, ROW3)
graveyard_surface = pg.Surface(ZONE_SIZE)
graveyard_surface.fill(GY_BG)
pg.draw.rect(graveyard_surface, BLACK, graveyard_surface.get_rect(), LINE_WIDTH)

mz1_1_rv = get_zonetyp_rv(COLUMN1, ROW4)
mz1_2_rv = get_zonetyp_rv(COLUMN2, ROW4)
mz1_3_rv = get_zonetyp_rv(COLUMN3, ROW4)
mz2_1_rv = get_zonetyp_rv(COLUMN1, ROW3)
mz2_2_rv = get_zonetyp_rv(COLUMN2, ROW3)
mz2_3_rv = get_zonetyp_rv(COLUMN3, ROW3)
mainzone_surface = pg.Surface(ZONE_SIZE)
mainzone_surface.fill(WHITE)
pg.draw.rect(mainzone_surface, BLACK, mainzone_surface.get_rect(), LINE_WIDTH)

sz1_1_rv = get_zonetyp_rv(COLUMN1, ROW5)
sz1_2_rv = get_zonetyp_rv(COLUMN2, ROW5)
sz1_3_rv = get_zonetyp_rv(COLUMN3, ROW5)
sz2_1_rv = get_zonetyp_rv(COLUMN1, ROW2)
sz2_2_rv = get_zonetyp_rv(COLUMN2, ROW2)
sz2_3_rv = get_zonetyp_rv(COLUMN3, ROW2)
subzone_surface = pg.Surface(ZONE_SIZE)
subzone_surface.fill(WHITE)
pg.draw.rect(subzone_surface, BLACK, subzone_surface.get_rect(), LINE_WIDTH)

row1_rv = [BOARD_MARGIN + ZONE_SIZE[0], ROW5, HALFBOARD_WIDTH - 2*ZONE_SIZE[0], ROW_HEIGHT - LINE_WIDTH]
row2_rv = [BOARD_MARGIN + ZONE_SIZE[0], ROW2 + LINE_WIDTH, HALFBOARD_WIDTH - 2*ZONE_SIZE[0], ROW_HEIGHT - LINE_WIDTH]
row_surface = pg.Surface((HALFBOARD_WIDTH - 2*ZONE_SIZE[0], ROW_HEIGHT - LINE_WIDTH), pg.SRCALPHA)
for x in range(HALFBOARD_WIDTH - 2*ZONE_SIZE[0]):
    d = abs(x - (HALFBOARD_WIDTH - 2*ZONE_SIZE[0])/2)
    transparancy = 1 - d/(HALFBOARD_WIDTH - 2*ZONE_SIZE[0])*2
    pg.draw.line(row_surface, (200, 200, 250, int(255*transparancy)), (x, 0), (x, ROW_HEIGHT - LINE_WIDTH))

hand_img = pg.Surface((HALFBOARD_WIDTH, ZONE_SIZE[1]))
hand_img.fill(WHITE)
hand1_center = [BOARD_MARGIN + HALFBOARD_WIDTH//2, ROW6 + ZONE_SIZE[1]//2]
hand2_center = [BOARD_MARGIN + HALFBOARD_WIDTH//2, ROW1 + ZONE_SIZE[1]//2]
# endregion

# region Indicator
TOTAL_POWER_FONT = pg.font.SysFont('Gulim', 20, italic=True)
TOTAL_POWER_DISTANCE = 40
total_power_2_pos = (BOARD_MARGIN + HALFBOARD_WIDTH//2 - TOTAL_POWER_DISTANCE, ROW_I + INDICATOR_HEIGHT//2 - 10)
total_power_1_pos = (BOARD_MARGIN + HALFBOARD_WIDTH//2 + TOTAL_POWER_DISTANCE, ROW_I + INDICATOR_HEIGHT//2 - 10)

MANA_ICON_SIZE = 14
MANA_ICON = {
    'R': pg.Surface((MANA_ICON_SIZE, MANA_ICON_SIZE), pg.SRCALPHA),
    'Y': pg.Surface((MANA_ICON_SIZE, MANA_ICON_SIZE), pg.SRCALPHA),
    'B': pg.Surface((MANA_ICON_SIZE, MANA_ICON_SIZE), pg.SRCALPHA)
}
pg.draw.circle(MANA_ICON['R'], MANA_R, (MANA_ICON_SIZE//2, MANA_ICON_SIZE//2), MANA_ICON_SIZE//2)
pg.draw.circle(MANA_ICON['Y'], MANA_Y, (MANA_ICON_SIZE//2, MANA_ICON_SIZE//2), MANA_ICON_SIZE//2)
pg.draw.circle(MANA_ICON['B'], MANA_B, (MANA_ICON_SIZE//2, MANA_ICON_SIZE//2), MANA_ICON_SIZE//2)

total_mana_surface = pg.Surface(ZONE_SIZE, pg.SRCALPHA)
total_mana_1_pos = (COLUMN_LEFT, ROW4 + ZONE_HEIGHT_FIX)
total_mana_2_pos = (COLUMN_RIGHT, ROW3 + ZONE_HEIGHT_FIX)
# endregion

# region Explanation
TITLE_FONT = pg.font.SysFont('Gulim', 40)
EXP_FONT = pg.font.SysFont('Gulim', 15)

title_pos = (WIDTH - RIGHT_MARGINE + 20, 30)
exp_pos = (title_pos[0] + 200, 100)
img_pos = (title_pos[0], 100)
# endregion

# region Endbutton
END_BUTTON_SIZE = (200, 100)
END_BUTTON_FONT = pg.font.SysFont('Gulim', 20)
end_button_rv = [WIDTH - END_BUTTON_SIZE[0] - 50, HEIGHT - END_BUTTON_SIZE[1] - 50, END_BUTTON_SIZE[0], END_BUTTON_SIZE[1]]
end_button = pg.Surface(END_BUTTON_SIZE)
end_button.fill(GY_BG)
end_button_label = END_BUTTON_FONT.render('End Turn', True, BLACK)
end_button.blit(end_button_label,
                (END_BUTTON_SIZE[0]//2 - end_button_label.get_width()//2,
                 END_BUTTON_SIZE[1]//2 - end_button_label.get_height()//2)
                )
# endregion

# real images on the board. May be different from real data.
gamecomponents: dict[TCG.GameComponent|Literal['endbutton'], pg.Rect] = {}

player1 = TCGplayer.player1
player2 = TCGplayer.player2
board = TCG.Board(player1, player2)

card_image_dict: dict[type[TCG.Card], pg.Surface] = {}
card_image_active_dict: dict[type[TCG.Card], pg.Surface] = {}
choice_image_dict: dict[str, pg.Surface] = {}
choice_image_dict['default'] = pg.image.load(os.path.join(root_dir, 'images', 'choice_default.png')).convert_alpha()
choice_image_dict['attack'] = pg.image.load(os.path.join(root_dir, 'images', 'choice_attack.png')).convert_alpha()

hovering = []
clicking = []
unclicking = []
making_subzone = 0

def is_card_revealed(card:TCG.Card):
    if isinstance(card.location, TCG.Deck):
        return False
    elif isinstance(card.location, TCG.Hand) and board.opponent() is card.location.halfboard:
        return False
    else:
        return True

def get_card_image(card:TCG.Card):
    if is_card_revealed(card):
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

        real_image = card_image_dict[type(card)] if card not in board.choosable['cards'] else card_image_active_dict[type(card)]

        # Draw variable values on each frame
        if card.power:
            real_image.blit(get_power_image(card.power), POWER_COORD)
        
        return real_image
    else:
        return card_back_active if card in board.choosable['cards'] else card_back_image

def get_button_image(button:TCG.Button):
    if button.image:
        if button.image in choice_image_dict:
            return choice_image_dict[button.image]
        else:
            try:
                choice_image_dict[button.image] = pg.image.load(button.image)
            except FileNotFoundError:
                choice_image_dict[button.image] = choice_image_dict['default']
        return choice_image_dict[button.image]
    else:
        return choice_image_dict['default']

def get_hovering_priority(hovering:list[TCG.GameComponent|TCG.Choice|str]) -> TCG.GameComponent|TCG.Choice|str|None:
    priority_order = [
        TCG.MainZone,
        TCG.Graveyard,
        TCG.Deck,
        TCG.HalfBoard,
        TCG.Board
    ]
    if 'endbutton' in hovering:
        return 'endbutton'
    else:
        cards = [key for key in hovering if isinstance(key, TCG.Card) and key != board.holding and key.is_active]
        if cards:
            return cards.pop()
        for type in priority_order:
            for key in hovering:
                if isinstance(key, type):
                    return key
    return None

def get_keys():
    def cards_to_card(cards:list[TCG.Card]):
        carddict:dict[TCG.Pack|TCG.Zone, list[TCG.Card]] = {}
        sorted_location = []
        result_card = None
        for card in cards:
            if board.holding is card:
                cards.remove(card)
                continue

            if card.location not in carddict:
                carddict[card.location] = []
            carddict[card.location].append(card)

        for loc in carddict:
            for loc_type in [TCG.Deck, TCG.Graveyard, TCG.Hand, TCG.Zone]:
                if isinstance(loc, loc_type):
                    sorted_location.append(loc)
                
        if sorted_location:
            location = sorted_location[0]
            if isinstance(location, TCG.Deck):
                pass
            elif isinstance(location, TCG.Graveyard):
                result_card = location.top()
            elif isinstance(location, TCG.Hand):
                for c in carddict[location]:
                    if not result_card:
                        result_card = c
                    elif location.cards.index(c) > location.cards.index(result_card):
                        result_card = c
            else:
                result_card = carddict[location].pop()

        return result_card

    keys:list[TCG.GameComponent|TCG.Effect|Literal['endbutton']] = []
    cards:list[TCG.Card] = []
    for key in gamecomponents:
        if gamecomponents[key].collidepoint(pg.mouse.get_pos()):
            if isinstance(key, TCG.Card):
                cards.append(key)
            elif isinstance(key, TCG.Board) or isinstance(key, TCG.HalfBoard):
                pass
            else:
                keys.append(key)

    card = cards_to_card(cards)
    if card:
        keys.append(card)
    return keys

def screen_generator():
    def board_generator():
        global gamecomponents
        gamecomponents = {}
        gamecomponents[board] = SURF.blit(board_surface, board_rv)
        gamecomponents[player1] = SURF.blit(halfboard_surface, half1_rv)
        gamecomponents[player2] = SURF.blit(halfboard_surface, half2_rv)
        SURF.blit(row_surface, row1_rv)
        SURF.blit(row_surface, row2_rv)
        gamecomponents[player1.deck] = SURF.blit(deck_surface, deck1_rv)
        gamecomponents[player2.deck] = SURF.blit(deck_surface, deck2_rv)
        gamecomponents[player1.graveyard] = SURF.blit(graveyard_surface, gy1_rv)
        gamecomponents[player2.graveyard] = SURF.blit(graveyard_surface, gy2_rv)
        gamecomponents[player1.mainzones[0]] = SURF.blit(mainzone_surface, mz1_3_rv)
        gamecomponents[player1.mainzones[1]] = SURF.blit(mainzone_surface, mz1_2_rv)
        gamecomponents[player1.mainzones[2]] = SURF.blit(mainzone_surface, mz1_1_rv)
        gamecomponents[player2.mainzones[0]] = SURF.blit(mainzone_surface, mz2_1_rv)
        gamecomponents[player2.mainzones[1]] = SURF.blit(mainzone_surface, mz2_2_rv)
        gamecomponents[player2.mainzones[2]] = SURF.blit(mainzone_surface, mz2_3_rv)
        gamecomponents[player1.subzones[0]] = SURF.blit(subzone_surface, sz1_3_rv)
        gamecomponents[player1.subzones[1]] = SURF.blit(subzone_surface, sz1_2_rv)
        gamecomponents[player1.subzones[2]] = SURF.blit(subzone_surface, sz1_1_rv)
        gamecomponents[player2.subzones[0]] = SURF.blit(subzone_surface, sz2_1_rv)
        gamecomponents[player2.subzones[1]] = SURF.blit(subzone_surface, sz2_2_rv)
        gamecomponents[player2.subzones[2]] = SURF.blit(subzone_surface, sz2_3_rv)
        gamecomponents[player1.hand] = SURF.blit(hand_img, card_on_zone(hand1_center), area=(0, 0, CARD_SIZE[0] + 20*(player1.hand.length - 1), ZONE_SIZE[1]))
        gamecomponents[player2.hand] = SURF.blit(hand_img, card_on_zone(hand2_center), area=(0, 0, CARD_SIZE[0] + 20*player2.hand.length, ZONE_SIZE[1]))
        gamecomponents['endbutton'] = SURF.blit(end_button, end_button_rv)

    def card_generator(card:TCG.Card, rv:list[int]|tuple[int, int], reversed:bool):
        '''rv: center!'''
        if board.holding is card:
            return False
        
        card_surface = get_card_image(card)
        is_turned = False
        if card.time:
            if 1 <= card.time <= 4:
                card_surface = pg.transform.rotate(get_card_image(card), 90*(card.time - 2))
                is_turned = True if card.time%2 else False
            else:
                raise Exception('Time error!')

        if reversed:
            card_surface = pg.transform.flip(card_surface, True, True)
        
        gamecomponents[card] = SURF.blit(card_surface, card_on_zone(rv, is_turned))
        return True
    
    def pack_generator(pack:TCG.Pack, reversed=False, margin:int=4):
        rv = list(gamecomponents[pack].center)
        for card in pack.cards:
            if card_generator(card, rv, reversed):
                rv[1] -= margin
    
    def hand_generator(hand:TCG.Hand, reversed=False, margin:int = 20):
        rv = list(gamecomponents[hand].center)
        rv[0] -= (len(hand.cards) - 1)*margin
        for card in hand.cards:
            card_generator(card, rv, reversed)
            rv[0] += margin
    
    def choice_generator():
        buttondict:dict[TCG.GameComponent, list[TCG.Button]] = {}
        # Find all active buttons
        for choice in board.active_choices:
            for drop in choice.drops:
                if isinstance(drop, TCG.Card):
                    pass
                elif isinstance(drop, TCG.Button):
                    if drop.bind_to in buttondict:
                        buttondict[drop.bind_to].append(drop)
                    else:
                        buttondict[drop.bind_to] = [drop]
        # Generate buttons
        for place, buttons in buttondict.items():
            button_rv = (gamecomponents[place].left + 2, gamecomponents[place].top + 80)
            margin = 85//(len(buttons) + 1)
            for i, button in enumerate(buttons):
                gamecomponents[button] = SURF.blit(get_button_image(button), (button_rv[0] + (i+1)*margin - 12, button_rv[1]))

    def info_generator():
        def mana_info_generator(surface:pg.Surface, player:TCG.HalfBoard):
            color_dict = {k: v for k, v in player.total_mana.items() if v != 0}

            x_interval = 2*MANA_ICON_SIZE
            x_begin = -2*MANA_ICON_SIZE
            y_interval = 2*MANA_ICON_SIZE
            y_begin = -0.5*(len(color_dict) - 1)*y_interval

            if not color_dict:
                return None

            for i, color in enumerate(color_dict):
                if color_dict[color] > 0:
                    for j in range(color_dict[color]):
                        surface.blit(MANA_ICON[color], 
                                (surface.get_width()//2 + x_begin + x_interval*j,
                                surface.get_height()//2 + y_begin + y_interval*i - MANA_ICON_SIZE//2)
                                )
            
        if player2.total_power is not None:
            SURF.blit(
                TOTAL_POWER_FONT.render(str(player2.total_power), True, DARK_RED),
                total_power_2_pos
            )
        if player1.total_power is not None:
            SURF.blit(
                TOTAL_POWER_FONT.render(str(player1.total_power), True, DARK_BLUE),
                total_power_1_pos
            )

        total_mana_1_surface = total_mana_surface.copy()
        total_mana_2_surface = total_mana_surface.copy()
        mana_info_generator(total_mana_1_surface, player1)
        mana_info_generator(total_mana_2_surface, player2)
        SURF.blit(total_mana_1_surface, total_mana_1_pos)
        SURF.blit(total_mana_2_surface, total_mana_2_pos)

    def explanation_generator():
        explanation = ['', '', None]

        def get_card_explanation(card:TCG.Card):
            title = card.name if card.name else 'Sample Card'
            discription = card.description if card.description else 'A dummy card for test.'
            img = get_card_image(card)
            return [title, discription, img]

        def get_gamecomponent_explanation(key:TCG.GameComponent|TCG.Choice|str):
            title = None
            discription = None
            img = None
            if key == None:
                pass
            elif isinstance(key, TCG.Board):
                title = 'Board'
                discription = 'Where game is played.'
            elif key == player1:
                title = 'Your Halfboard'
                discription = 'Your side of the board.'
            elif key == player2:
                title = "Opponent's Halfboard"
                discription = "The opponent's side of the board"
            elif key == player1.deck:
                title = 'Your Deck'
                discription = 'Your Deck.'
            elif isinstance(key, TCG.MainZone):
                title = key.name
                discription = 'Your Main Zone.'
            elif key == player1.graveyard:
                title = 'Your Graveyard'
                discription = 'Used cards are here.'
            elif isinstance(key, TCG.SubZone):
                title = key.name
                discription = 'Your Sub Zone.'
            elif key == 'temp zone':
                title = 'New Sub Zone'
                discription = 'Place card here to create new Sub Zone.'
            elif key == 'endbutton':
                title = 'End Button'
                discription = "For Debug. Only active when opponent's turn."
            return [title, discription, img]

        key = get_hovering_priority(hovering)
        if key:
            explanation = get_card_explanation(key) \
                          if isinstance(key, TCG.Card) \
                          else get_gamecomponent_explanation(key)
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
    # ROW2
    pack_generator(player2.deck, reversed=True)
    for subzone in player2.subzones:
        if subzone.card:
            card_generator(subzone.card, gamecomponents[subzone].center, reversed=True)
    # ROW3
    pack_generator(player2.graveyard, reversed=True)
    for mainzone in player2.mainzones:
        if mainzone.card:
            card_generator(mainzone.card, gamecomponents[mainzone].center, reversed=True)
    # ROW5
    for subzone in player1.subzones:
        if subzone.card:
            card_generator(subzone.card, gamecomponents[subzone].center, reversed=False)
    pack_generator(player1.deck)
    # ROW4
    for mainzone in player1.mainzones:
        if mainzone.card:
            card_generator(mainzone.card, gamecomponents[mainzone].center, reversed=False)
    pack_generator(player1.graveyard)
    # HAND
    hand_generator(player1.hand)
    hand_generator(player2.hand, reversed=True)

    if isinstance(board.holding, TCG.Card):
        gamecomponents[board.holding] = SURF.blit(
            get_card_image(board.holding) if isinstance(board.holding, TCG.Card) else card_back_image,
            tuple(sum(elem) for elem in zip(pg.mouse.get_pos(), (-50, -70)))
            )
    
    choice_generator()
    info_generator()
    explanation_generator()

# Start
gameplay = board.IO()
next(gameplay)
refresh = True

def calculate(message:tuple[Literal['click', 'drop', 'rightclick'], list]):
    return gameplay.send(message)

screen_generator()

while refresh:
    frame_clicking = []
    unclicking = []
    for event in pg.event.get():
        if event.type == pg.QUIT:
            refresh = False
            continue

        if event.type == pg.MOUSEMOTION:
            # Initialize hovering (As you moved.)
            hovering = []
            for key in gamecomponents:
                if gamecomponents[key].collidepoint(pg.mouse.get_pos()):
                    #print(f'you are on {key}.')
                    hovering.append(key)

        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 3:
                calculate(('rightclick', []))
            elif not board.holding:
                calculate(('click', get_keys()))
            else:
                raise Exception('Tryed to click while dragging.')

        if event.type == pg.MOUSEBUTTONUP:
            if event.button == 3:
                pass
            else:
                print('unpressed')
                ans = calculate(('drop', get_keys()))
                if ans:
                    refresh = False
                    continue

    screen_generator()
    pg.display.update()

SURF.fill(WHITE)
winner = board.opponent(board.loser).name if isinstance(board.loser, TCG.HalfBoard) else None
gameover_message = TITLE_FONT.render(f'{winner} Survives!', True, BLACK)
SURF.blit(gameover_message, (SURF.get_width()//2 - gameover_message.get_width()//2,
                             SURF.get_height()//2 - gameover_message.get_height()//2))
pg.display.update()

watching = True
while watching:
    for event in pg.event.get():
        if event.type in [pg.QUIT, pg.MOUSEBUTTONDOWN, pg.MOUSEBUTTONUP]:
            watching = False

pg.quit()
sys.exit()