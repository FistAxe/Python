import pygame as pg
import sys
import os
from typing import Union, Literal

root_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(root_dir)
import TCG
import TCGplayer

pg.init()

WIDTH = 1280
HEIGHT = 768

COLORS = {
    'WHITE' : pg.Color(255, 255, 255),
    'BLACK' : pg.Color(0, 0, 0),
    'DARK_BLUE' : pg.Color(50, 50, 100),
    'DARK_RED' : pg.Color(100, 50, 50),
    'BOARD_BG' : pg.Color(230, 230, 255),
    'ROW_BG' : pg.Color(200, 200, 255),
    'GY_BG' : pg.Color(200, 200, 200),

    'MANA_R' : pg.Color(255, 50, 50),
    'MANA_Y' : pg.Color(200, 200, 50),
    'MANA_B' : pg.Color(50, 50, 255),
        }

# Screen Init
SURF = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption('TCG')
SURF.fill(COLORS['WHITE'])

FPS = pg.time.Clock()

# region Layout
RIGHT_MARGINE = 500
BOARD_MARGIN = 5
BOARD_WIDTH = WIDTH - RIGHT_MARGINE - 2*BOARD_MARGIN
LINE_WIDTH = 3
CARD_SIZE = (90, 135)
ZONE_MARGIN = 2
ZONE_SIZE = (CARD_SIZE[0] + 2*ZONE_MARGIN, CARD_SIZE[1] + 2*ZONE_MARGIN)
GRID_MARGINE = 5
GRID_SIZE = (CARD_SIZE[0] + 2*GRID_MARGINE, CARD_SIZE[1] + 2*GRID_MARGINE)
COLUMN_SPACING = 5
ROW_SPACING = 20

ROW_MIDDLE = HEIGHT//2

ROW_UP = ROW_MIDDLE - GRID_SIZE[1] - ROW_SPACING
ROW_DOWN = ROW_MIDDLE + GRID_SIZE[1] + ROW_SPACING

COLUMN_LEFT = BOARD_MARGIN + GRID_SIZE[0]//2
COLUMN_RIGHT = BOARD_MARGIN + BOARD_WIDTH - GRID_SIZE[0]//2

HAND_SPACING = 20
PILE_SPACING = 4
# endregion

# region Card
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
NAME_FONT = pg.font.SysFont('Gulim', 10)
POWER_FONT = pg.font.SysFont('Segoe UI Black', 16, italic=True)
SPEED_FONT = pg.font.SysFont('Verdana', 13, bold=True)
NAME_COORD = (1, 1)
IMAGE_COORD = (0, 11)
POWER_COORD = (2, CARD_SIZE[1] - 20)
SPEED_COORD = (2, CARD_SIZE[1] - 40)
power_dict: dict[int, pg.Surface] = {}
speed_dict: dict[int, pg.Surface] = {}
speed_dict[1] = SPEED_FONT.render('I', False, COLORS['BLACK'])
speed_dict[2] = SPEED_FONT.render('II', False, COLORS['BLACK'])
speed_dict[3] = SPEED_FONT.render('III', False, COLORS['BLACK'])
speed_dict[4] = SPEED_FONT.render('IV', False, COLORS['BLACK'])
speed_dict[5] = SPEED_FONT.render('V', False, COLORS['BLACK'])
speed_dict[6] = SPEED_FONT.render('VI', False, COLORS['BLACK'])
speed_dict[7] = SPEED_FONT.render('VII', False, COLORS['BLACK'])
speed_dict[8] = SPEED_FONT.render('VIII', False, COLORS['BLACK'])
speed_dict[9] = SPEED_FONT.render('IX', False, COLORS['BLACK'])
speed_dict[10] = SPEED_FONT.render('X', False, COLORS['BLACK'])


def get_power_image(power:int):
    if power not in power_dict:
        power_dict[power] = POWER_FONT.render(str(power), False, COLORS['BLACK'])
    return power_dict[power]

def get_speed_image(speed:int):
    if speed not in speed_dict:
        speed_dict[speed] = SPEED_FONT.render(str(speed), False, COLORS['BLACK'])
    return speed_dict[speed]
# endregion

def topleft(center:tuple[int, int], size:Literal['GRID', 'ZONE', 'CARD']):
    if size == 'CARD':
        halfwidth = CARD_SIZE[0]//2
        halfheight = CARD_SIZE[1]//2
    elif size == 'ZONE':
        halfwidth = ZONE_SIZE[0]//2
        halfheight = ZONE_SIZE[1]//2
    else:
        halfwidth = GRID_SIZE[0]//2
        halfheight = GRID_SIZE[1]//2
    return (center[0] - halfwidth, center[1] - halfheight)

# region Board
# rv is topleft!
deck1_rv = topleft((COLUMN_RIGHT, ROW_DOWN), size='ZONE')
deck2_rv = topleft((COLUMN_LEFT, ROW_UP), size='ZONE')
deck_surface = pg.Surface(ZONE_SIZE)
deck_surface.fill(COLORS['WHITE'])
pg.draw.rect(deck_surface, COLORS['BLACK'], deck_surface.get_rect(), LINE_WIDTH)

gy1_rv = topleft((COLUMN_RIGHT, ROW_MIDDLE), size='ZONE')
gy2_rv = topleft((COLUMN_LEFT, ROW_MIDDLE), size='ZONE')
graveyard_surface = pg.Surface(ZONE_SIZE)
graveyard_surface.fill(COLORS['GY_BG'])
pg.draw.rect(graveyard_surface, COLORS['BLACK'], graveyard_surface.get_rect(), LINE_WIDTH)

row_rv = (BOARD_MARGIN + ZONE_SIZE[0], HEIGHT//2 - ZONE_SIZE[1]//2)
row_surface = pg.Surface((BOARD_WIDTH - 2*ZONE_SIZE[0], ZONE_SIZE[1]), pg.SRCALPHA)
for x in range(BOARD_WIDTH - 2*ZONE_SIZE[0]):
    d = abs(x - (BOARD_WIDTH - 2*ZONE_SIZE[0])/2)
    transparancy = 1 - d/(BOARD_WIDTH - 2*ZONE_SIZE[0])*2
    pg.draw.line(row_surface, (200, 200, 250, int(255*transparancy)), (x, 0), (x, ZONE_SIZE[1] - LINE_WIDTH))

zone_surface = pg.Surface(ZONE_SIZE)
zone_surface.fill(COLORS['WHITE'])
pg.draw.rect(zone_surface, COLORS['BLACK'], zone_surface.get_rect(), LINE_WIDTH)

hand1_center = (BOARD_MARGIN + BOARD_WIDTH//2, HEIGHT - ZONE_SIZE[1]//2 - BOARD_MARGIN)
hand2_center = (BOARD_MARGIN + BOARD_WIDTH//2, BOARD_MARGIN + ZONE_SIZE[1]//2)
# endregion

# region Indicator
TOTPOWER_FONT = pg.font.SysFont('Gulim', 20)
# endregion

# region Explanation
TITLE_FONT = pg.font.SysFont('Gulim', 40)
EXP_FONT = pg.font.SysFont('Gulim', 15)

title_pos = (WIDTH - RIGHT_MARGINE + 20, 30)
exp_pos = (title_pos[0] + 200, 100)
img_pos = (title_pos[0], 100)
# endregion

# region Background
background = pg.Surface((WIDTH, HEIGHT))
background.fill(COLORS['WHITE'])
background.blits((
    (deck_surface, deck1_rv),
    (deck_surface, deck2_rv),
    (graveyard_surface, gy1_rv),
    (graveyard_surface, gy2_rv),
    (row_surface, row_rv)
))
background = background.convert()
# endregion

# Game Board Init
player1 = TCGplayer.player1
player2 = TCGplayer.player2
game = TCG.Game(player1, player2)

card_image_dict: dict[type[TCG.Card], pg.Surface] = {}
card_image_active_dict: dict[type[TCG.Card], pg.Surface] = {}

hovering = set()
top_hovering = None
holding = None
choices : list[TCG.Choice] = []

fixed_rects : dict[TCG.GameComponent, pg.Rect] = {
    game.row : pg.Rect(row_rv, row_surface.get_size()),
    game.deck[player1] : pg.Rect(deck1_rv, ZONE_SIZE),
    game.deck[player2] : pg.Rect(deck2_rv, ZONE_SIZE),
    game.graveyard[player1] : pg.Rect(gy1_rv, ZONE_SIZE),
    game.graveyard[player2] : pg.Rect(gy2_rv, ZONE_SIZE),
        }
rects = fixed_rects.copy()

# region VFX
class Vfx:
    _duration : float
    lifetime : float = 0

    def __init__(self) -> None:
        self.lifetime = self._duration
    
    def update(self, dt:float):
        self.lifetime -= dt

vfx_list : list[Vfx] = []
# endregion

def get_colliding_rect_keys():
    return {key for key in rects if rects[key].collidepoint(pg.mouse.get_pos())}

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
                name = NAME_FONT.render(card.name, False, COLORS['BLACK'])
                real_image_bg.blit(name, NAME_COORD)
                real_image_active_bg.blit(name, NAME_COORD)

            card_image_dict[type(card)] = real_image_bg.convert()
            card_image_active_dict[type(card)] = real_image_active_bg.convert()


        if any((choice['source'] is card for choice in choices)):
            real_image = card_image_active_dict[type(card)]
        else:
            real_image = card_image_dict[type(card)]

        # Draw variable values on each frame
        if card.power:
            real_image.blit(get_power_image(card.power), POWER_COORD)
        
        return real_image
    
    else:
        if any((choice['source'] is card for choice in choices)):
            return card_back_active
        else:
            return card_back_image

def get_hovering_priority() -> TCG.GameComponent|None:
    global hovering, holding
    #if hovering:
        #print(hovering)
    priority_order = {
        TCG.Deck : 0,
        TCG.Card : 1,
        TCG.Graveyard : 2,
        TCG.Column : 3,
        TCG.Row.NewColumn : 4,
        TCG.Hand : 5,
    }

    piles = list({key for key in hovering if isinstance(key, TCG.Pile)})
    for pile in sorted(piles, key=lambda k: priority_order[type(k)]):
        cards = [card for card in hovering if isinstance(card, TCG.Card) and card.location is pile]
        for card in reversed(pile.cards):
            if card in cards:
                return card
        return pile
    
    return None

def get_key(drag:bool):
    global holding
    source_target = 'source' if drag else 'target'
    keys = get_colliding_rect_keys() & {choice[source_target] for choice in choices}
    cards = {key for key in keys if isinstance(key, TCG.Card) and not holding}
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
                        break
    elif len(piles) == 1:
        key = piles.pop()
    else:
        key = None
    
    holding = key if drag else None
    print(f'{"clicked" if drag else "dropped"} {"something" if key else "Nothing"}.')
    return key

def screen_generator():
    global rects

    def _card_generator(card:TCG.Card, center:tuple[int, int], reversed:bool):
        if card is holding:
            return False
        
        card_surface = get_card_image(card)
        if reversed:
            card_surface = pg.transform.flip(card_surface, True, True)
        
        rects[card] = SURF.blit(card_surface, topleft(center, size='CARD'))
        return True
    
    def _pile_generator(pile:TCG.Pile, reversed=False):
        center = rects[pile].center
        spacing = 0
        for card in pile.cards:
            if _card_generator(card, (center[0], center[1] - spacing), reversed):
                spacing -= PILE_SPACING
    
    def _hand_generator(player:TCG.Player, reversed=False):
        hand = game.hand[player]
        tot_hand_width = CARD_SIZE[0] + (hand.length - 1)*HAND_SPACING
        hand_center = hand1_center if player is player1 else hand2_center
        
        rects[hand] = pg.Rect((hand_center[0] - tot_hand_width//2, hand_center[1] - CARD_SIZE[1]//2),
                                           (tot_hand_width, CARD_SIZE[1]))
        spacing = 0
        for card in hand.cards:
            _card_generator(card, (rects[hand].left + CARD_SIZE[0]//2 + spacing, rects[hand].centery), reversed)
            spacing += HAND_SPACING

    def _column_generator():
        def set_column_rects(columns:list):
            increment = GRID_SIZE[0] + COLUMN_SPACING
            for i, column in enumerate(columns):
                center = (BOARD_MARGIN + BOARD_WIDTH//2 - int(((len(columns)-1)/2 - i)*increment), ROW_MIDDLE)
                rects[column] = pg.Rect(topleft(center, size='GRID'), (GRID_SIZE[0], GRID_SIZE[1]))
        
        columns = game.row.columns.copy()
        set_column_rects(columns)
        if game.row in hovering and game.row.new_column:
            x, y = pg.mouse.get_pos()
            for i, column in enumerate(columns):
                if rects[column].collidepoint(x, y):
                    break
                elif x < rects[column].left:
                    game.row.new_column.index = i
                    columns.insert(i, game.row.new_column)
                    break
            else:
                game.row.new_column.index = len(columns)
                columns.append(game.row.new_column)
            set_column_rects(columns)

        for column in columns:
            SURF.blit(zone_surface, topleft(rects[column].center, size='ZONE'))
            for card in column.cards:
                updown_spacing = -20 if card.owner is player1 else 20
                activated_spacing = -5 if card.owner is player1 else 5
                center = (rects[column].centerx, rects[column].centery + updown_spacing + activated_spacing)
                _card_generator(card, center, card.owner is player2)

    def _indicator_generator():
        for column in game.row.columns:
            pow1 = TOTPOWER_FONT.render(f'{column.col_power(player1)}', False, COLORS['DARK_BLUE'])
            pow2 = TOTPOWER_FONT.render(f'{column.col_power(player2)}', False, COLORS['DARK_RED'])
            rect1 = (rects[column].centerx - pow1.get_width()//2, ROW_DOWN - pow1.get_height()//2)
            rect2 = (rects[column].centerx - pow2.get_width()//2, ROW_UP - pow2.get_height()//2)
            SURF.blit(pow1, rect1)
            SURF.blit(pow2, rect2)

        totpow1 = TOTPOWER_FONT.render(f'Σ = {game.tot_power(player1)}', False, COLORS['DARK_BLUE'])
        totpow2 = TOTPOWER_FONT.render(f'Σ = {game.tot_power(player2)}', False, COLORS['DARK_RED'])
        rect1 = (COLUMN_LEFT - totpow1.get_width()//2, ROW_DOWN - totpow1.get_height()//2)
        rect2 = (COLUMN_RIGHT - totpow2.get_width()//2, ROW_UP - totpow2.get_height()//2)
        SURF.blit(totpow1, rect1)
        SURF.blit(totpow2, rect2)

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

        key = top_hovering
        if key:
            if isinstance(key, TCG.Card):
                explanation = get_card_explanation(key)
            else:
                explanation = get_gamecomponent_explanation(key)
        else:
            explanation = ['No hovering', '', None]

        rendered_title = TITLE_FONT.render(explanation[0], True, COLORS['BLACK'])
        rendered_explanation = EXP_FONT.render(explanation[1], True, COLORS['BLACK'])
        rendered_img = pg.transform.scale(explanation[2], (180, 240)) if explanation[2] != None else None

        SURF.blit(rendered_title, title_pos)
        SURF.blit(rendered_explanation, exp_pos)
        if rendered_img:
            SURF.blit(rendered_img, img_pos)

    # Screen Reset
    SURF.blit(background, (0, 0))
    rects = fixed_rects.copy()

    # Variable Rects
    _column_generator()

    for pile in [game.deck[player2], game.graveyard[player2]]:
        _pile_generator(pile, reversed=True)

    for pile in [game.graveyard[player1], game.deck[player1]]:
        _pile_generator(pile, reversed=False)

    # HAND
    _hand_generator(player1)
    _hand_generator(player2, reversed=True)

    _indicator_generator()
    _explanation_generator()

    if isinstance(holding, TCG.Card):
        rects[holding] = SURF.blit(
            get_card_image(holding),
            tuple(sum(elem) for elem in zip(pg.mouse.get_pos(), (-50, -70)))
            )



# Start
gameplay = game.IO()
next(gameplay)
refresh = True
reason = None

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
        dt = FPS.tick(60) / 1000
        screen_generator()
        # --- VFX MODE ---
        if vfx_list:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    refresh = False
                    continue
                if event.type == pg.MOUSEBUTTONDOWN:
                    vfx_list.clear() # Skip all visual effects
                    continue
        
            else:
                # Update and draw all active VFX
                for vfx in vfx_list:
                    vfx.update(dt)
                vfx_list = [v for v in vfx_list if v.lifetime > 0]
        
        else:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    refresh = False
                    continue

                if event.type == pg.MOUSEMOTION:
                    # Initialize hovering (As you moved.)
                    hovering = get_colliding_rect_keys()
                    top_hovering = get_hovering_priority()

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

        pg.display.update()

except StopIteration as e:
    reason = (e.value)

SURF.fill(COLORS['WHITE'])
gameover_message = TITLE_FONT.render(f'{game.opponent(game.current_player).name} Survives!', True, COLORS['BLACK'])
gameover_reason = EXP_FONT.render(reason, True, COLORS['BLACK'])
SURF.blit(gameover_message, (SURF.get_width()//2 - gameover_message.get_width()//2,
                             SURF.get_height()//2 - gameover_message.get_height()//2))
SURF.blit(gameover_reason, (SURF.get_width()//2 - gameover_reason.get_width()//2,
                            SURF.get_height()//2 + gameover_message.get_height() + gameover_reason.get_height()//2))
pg.display.update()

watching = True
while watching:
    for event in pg.event.get():
        if event.type in [pg.QUIT, pg.MOUSEBUTTONDOWN]:
            watching = False

pg.quit()
sys.exit()