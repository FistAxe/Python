import pygame as pg
import sys
import TCG
import TCGplayer
from typing import Union, Literal

pg.init()

# Screen Size
WIDTH = 1280
HEIGHT = 768

# Color Definition
WHITE = pg.Color(255, 255, 255)
BLACK = pg.Color(0, 0, 0)
BOARD_BG = pg.Color(230, 230, 255)
ROW_BG = pg.Color(200, 200, 255)
GY_BG = pg.Color(200, 200, 200)

# Screen Init
SURF = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption('TCG')
SURF.fill(WHITE)

FPS = pg.time.Clock()
FPS.tick(60)

# Layout Definition
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

# Card Definition
CARD_SIZE = [90, 120]
CARD_NAME_HEIGHT = 12
card_back_image = pg.image.load('./images/card_back.png').convert()
card_front_image = pg.image.load('./images/card_front.png').convert()
card_front_active = pg.image.load('./images/card_front_active.png').convert()
card_front_R = pg.image.load('./images/card_front_R.png').convert()
card_front_R_active = pg.image.load('./images/card_front_R_active.png').convert()
card_front_Y = pg.image.load('./images/card_front_Y.png').convert()
card_front_Y_active = pg.image.load('./images/card_front_Y_active.png').convert()
card_front_B = pg.image.load('./images/card_front_B.png').convert()
card_front_B_active = pg.image.load('./images/card_front_B_active.png').convert()


# Card Fonts
NAME_FONT = pg.font.SysFont('Gulim', 11)
POWER_FONT = pg.font.SysFont('Segoe UI Black', 16, italic=True)
SPEED_FONT = pg.font.SysFont('Verdana', 13, bold=True)
NAME_COORD = (14, 1)
IMAGE_COORD = (2, 13)
POWER_COORD = (4, 98)
SPEED_COORD = (4, 70)
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

def get_power_image(power:int):
    if power not in power_dict:
        power_dict[power] = POWER_FONT.render(str(power), False, BLACK)
    return power_dict[power]

def get_speed_image(speed:int):
    if speed not in speed_dict:
        speed_dict[speed] = SPEED_FONT.render(str(speed), False, BLACK)
    return speed_dict[speed]

# Zone Definition
ZONE_MARGIN = 2
ZONE_SIZE = [CARD_SIZE[0] + 2*ZONE_MARGIN, CARD_SIZE[1] + 2*ZONE_MARGIN]
SUBZONE_MARGIN = 30

def card_on_zone(zone_pos):
    return [zone_pos[0] + ZONE_MARGIN, zone_pos[1] + ZONE_MARGIN]

# Game Components RectValues & Images
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
    pg.draw.line(row1, (200, 200, 250, int(255*transparancy)), (x, 0), (x, ROW_HEIGHT - LINE_WIDTH))
row2 = row1.copy()

hand_img = pg.Surface((10, 10))
hand_img.fill(WHITE)
hand1_center = [BOARD_MARGIN + HALFBOARD_WIDTH//2 - ZONE_SIZE[0]//2, ROW6]
hand2_center = [BOARD_MARGIN + HALFBOARD_WIDTH//2 - ZONE_SIZE[0]//2, ROW1]

# Explanation
TITLE_FONT = pg.font.SysFont('Gulim', 40)
EXP_FONT = pg.font.SysFont('Gulim', 15)

title_pos = (WIDTH - RIGHT_MARGINE + 20, 30)
exp_pos = (title_pos[0] + 200, 100)
img_pos = (title_pos[0], 100)

# For Debugging
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


# real images on the board. May be different from real data.
gamecomponents: dict[TCG.GameComponent|TCG.Choice|Literal['temp zone', 'endbutton'], pg.Rect] = {}

player1 = TCGplayer.player1
player2 = TCGplayer.player2
board = TCG.Board(player1, player2)

card_image_dict: dict[type[TCG.Card], pg.Surface] = {}
card_image_active_dict: dict[type[TCG.Card], pg.Surface] = {}
choice_image_dict: dict[str, pg.Surface] = {}
choice_image_dict['default'] = pg.image.load('./images/choice_default.png').convert_alpha()
choice_image_dict['attack'] = pg.image.load('./images/choice_attack.png').convert_alpha()

hovering = []
clicking = []
unclicking = []
making_subzone = 0

def get_card_image(card:TCG.Card):
    if card.on_face:
        # Use premade image for background
        if type(card) not in card_image_dict:
            # Make one.
            if card.color == 'R':
                real_image_bg = card_front_R.copy()
                real_image_bg_active = card_front_R_active.copy()
            elif card.color == 'Y':
                real_image_bg = card_front_Y.copy()
                real_image_bg_active = card_front_Y_active.copy()
            elif card.color == 'B':
                real_image_bg = card_front_B.copy()
                real_image_bg_active = card_front_B_active.copy()
            else:
                real_image_bg = card_front_image.copy()
                real_image_bg_active = card_front_active.copy()
            
            if card.image:
                img = pg.image.load(card.image).convert()
                real_image_bg.blit(img, IMAGE_COORD)
                real_image_bg_active.blit(img, IMAGE_COORD)
            if card.name:
                name = NAME_FONT.render(card.name, False, BLACK)
                real_image_bg.blit(name, NAME_COORD)
                real_image_bg_active.blit(name, NAME_COORD)

            card_image_dict[type(card)] = real_image_bg.convert()
            card_image_active_dict[type(card)] = real_image_bg_active.convert()

        if card.active == 'active':
            real_image = card_image_active_dict[type(card)]
        else:
            real_image = card_image_dict[type(card)]

        # Draw variable values on each frame
        if card.power:
            real_image.blit(get_power_image(card.power), POWER_COORD)
        if card.speed:
            real_image.blit(get_speed_image(card.speed), SPEED_COORD)
        
        return real_image
    else:
        return card_back_image

def get_choice_image(choice:TCG.Choice):
    if choice.image:
        if choice.image in choice_image_dict:
            return choice_image_dict[choice.image]
        else:
            try:
                choice_image_dict[choice.image] = pg.image.load(choice.image)
            except FileNotFoundError:
                choice_image_dict[choice.image] = choice_image_dict['default']
        return choice_image_dict[choice.image]
    else:
        return choice_image_dict['default']

def get_hovering_priority(hovering:list[TCG.GameComponent|TCG.Choice|str]) -> TCG.GameComponent|TCG.Choice|str|None:
    priority_order = [
        TCG.MainZone,
        TCG.Graveyard,
        TCG.Deck,
        TCG.Row,
        TCG.HalfBoard,
        TCG.Board
    ]
    if 'temp zone' in hovering:
        return 'temp zone'
    elif 'endbutton' in hovering:
        return 'endbutton'
    else:
        cards = [key for key in hovering if isinstance(key, TCG.Card) and key != board.holding and key.on_face]
        if cards:
            return cards.pop()
        for type in priority_order:
            for key in hovering:
                if isinstance(key, type):
                    return key
    return None

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

    def pack_generator():
        def card_generator(card, rv:list[int]|tuple[int, int], reversed:bool, i:int, margin:int=4):
            card_surface = get_card_image(card)
            dir = -1 if reversed else 1
            if reversed:
                card_surface = pg.transform.flip(card_surface, True, True)
            gamecomponents[card] = SURF.blit(card_surface,
                                             (card_on_zone(rv)[0], card_on_zone(rv)[1] + dir*margin*i))
            return gamecomponents[card]
        
        def choice_generator(card:TCG.Card):
            if choices := [choice for choice in board.current_player.available_choices
                           if choice.effect.bind_to == card and choice.is_button]:
                choice_rv = (gamecomponents[card].left + 2, gamecomponents[card].top + 80)
                margin = 85//(len(choices) + 1)
                for i, choice in enumerate(choices):
                    gamecomponents[choice] = SURF.blit(get_choice_image(choice),
                                                       (choice_rv[0] + (i+1)*margin - 12, choice_rv[1]))

        cards_shown_dict: dict[TCG.GameComponent, list[TCG.Card]] = {}
        for key in gamecomponents:
            # Ignore cardlist generation on temp zone
            if isinstance(key, TCG.Pack) or isinstance(key, TCG.Hand):
                cards_shown_dict[key] = key._cards.copy()
        # Holding card is not shown on its place
        if board.holding_from in cards_shown_dict and board.holding in cards_shown_dict[board.holding_from]:
            cards_shown_dict[board.holding_from].remove(board.holding)

        # ROW2
        for subzone in [key for key in gamecomponents if isinstance(key, TCG.SubZone) and key.halfboard == player2]:
            for i, card in enumerate(cards_shown_dict[subzone]):
                card_generator(card, gamecomponents[subzone].topleft, True, i, CARD_NAME_HEIGHT)
            choice_generator(card)

        for i, card in enumerate(cards_shown_dict[player2.deck]):
            card_generator(card, gamecomponents[player2.deck].topleft, True, i)
        # ROW3
        for i, card in enumerate(cards_shown_dict[player2.graveyard]):
            card_generator(card, gamecomponents[player2.graveyard].topleft, True, i)
        for i, card in enumerate(cards_shown_dict[player2.main_zone]):
            card_generator(card, gamecomponents[player2.main_zone].topleft, True, i, CARD_NAME_HEIGHT)
        choice_generator(card)
        # ROW5
        for subzone in [key for key in gamecomponents if isinstance(key, TCG.SubZone) and key.halfboard == player1]:
            for i, card in enumerate(cards_shown_dict[subzone]):
                card_generator(card, gamecomponents[subzone].topleft, False, i, CARD_NAME_HEIGHT)
            choice_generator(card)
        for i, card in enumerate(cards_shown_dict[player1.deck]):
            card_generator(card, gamecomponents[player1.deck].topleft, False, i)
        # ROW4
        for i, card in enumerate(cards_shown_dict[player1.main_zone]):
            card_generator(card, gamecomponents[player1.main_zone].topleft, False, i, CARD_NAME_HEIGHT)
        choice_generator(card)

        for i, card in enumerate(cards_shown_dict[player1.graveyard]):
            card_generator(card, gamecomponents[player1.graveyard].topleft, False, i)
        # HAND
        for i, card in enumerate(cards_shown_dict[player1.hand]):
            gamecomponents[card] = SURF.blit(get_card_image(card),
                                             (card_on_zone(hand1_center)[0] - len(cards_shown_dict[player1.hand]) + i*20, card_on_zone(hand1_center)[1])
                                             )
        for i, card in enumerate(cards_shown_dict[player2.hand]):
            gamecomponents[card] = SURF.blit(pg.transform.flip(card_back_image, True, True),
                                             (card_on_zone(hand2_center)[0] - len(cards_shown_dict[player2.hand]) + i*20, card_on_zone(hand2_center)[1])
                                             )

        if isinstance(board.holding, TCG.Card):
            gamecomponents[board.holding] = SURF.blit(
                get_card_image(board.holding) if isinstance(board.holding, TCG.Card) else card_back_image,
                tuple(sum(elem) for elem in zip(pg.mouse.get_pos(), (-50, -70)))
                )

    def explanation_generator():
        explanation = ['', '', None]

        def get_card_explanation(card:TCG.Card):
            title = card.name if card.name else 'Sample Card'
            discription = card.discription if card.discription else 'A dummy card for test.'
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
            elif key == player1.row:
                title = 'Your Row'
                discription = 'Place here to make a new Sub Zone.'
            elif key == player1.main_zone:
                title = 'Main Zone'
                discription = 'Place here to end turn.'
            elif key == player1.graveyard:
                title = 'Your Graveyard'
                discription = 'Used cards are here.'
            elif isinstance(key, TCG.SubZone):
                title = f'Your Sub Zone {key.name}'
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
    subzone_generator()
    pack_generator()
    explanation_generator()

# Start
gameplay = board.play()
next(gameplay)
refresh = True

def calculate(message:tuple[Literal['click', 'drop'], list, int|None]):
    return gameplay.send(message)

screen_generator()

class EndException(Exception):
    pass

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
                    #Sprint(f'you are on {key}.')
                    hovering.append(key)
            
            # Below is only for subzone indexing.
            if board.current_player == player1 and board.holding and len(board.current_player.row.subzones) < 3:
                # On row, but not on Subzone.
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
                # On Subzone -> Initialize making_subzone.
                else:
                    making_subzone = 0

        if event.type == pg.MOUSEBUTTONDOWN:
            # print('pressed')
            if not board.holding:
                keys = []
                for key in gamecomponents:
                    if gamecomponents[key].collidepoint(pg.mouse.get_pos()):
                        #print(f'you clicked {key}.')
                        keys.append(key)
                calculate(('click', keys, None))
            else:
                raise Exception('Tryed to click while dragging.')

        if event.type == pg.MOUSEBUTTONUP:
            print('unpressed')
            keys = []
            for key in gamecomponents:
                if gamecomponents[key].collidepoint(pg.mouse.get_pos()):
                    #print(f'you unclicked {key}.')
                    keys.append(key)
            if board.holding:
                try:
                    ans = calculate(('drop', keys, making_subzone))
                    if ans == False:
                        raise Exception('Something went Wrong')
                    elif isinstance(ans, str):
                        if ans == 'end!':
                            raise EndException()
                        else:
                            raise Exception(ans)
                except EndException:
                    refresh = False
            making_subzone = 0

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