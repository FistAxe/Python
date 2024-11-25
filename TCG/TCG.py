from typing import Callable, Literal
LOSE = 'lose'

class Card:
    effects: list['Effect']
    def __init__(self, name='default card', *effects):
        self.name = name
        self.effects = []
        if effects != ():
            for effect in effects:
                self.effects.append(effect)

class Creature(Card):
    def __init__(self, name='default creature', power=1, speed=None, *effects):
        super().__init__(name)
        self.power = power
        self.speed = speed

class Spell(Card):
    def __init__(self, name='default spell', speed=1):
        super().__init__(name)
        self.speed = speed

class Artifact(Card):
    def __init__(self, name='default artifact', speed=None):
        super().__init__(name)
        self.speed = speed

class Effect():
    def __init__(self, condition):
        self.condition = condition

class Zone:
    def __init__(self, halfboard:'HalfBoard'):
        self.name = 'error: not specific zone'
        self.cards: list[Card] = []
        self.halfboard = halfboard

class Deck:
    def __init__(self, halfboard):
        self.cards: list[Card] = []
        self.halfboard = halfboard

    def pop(self, num):
        try:
            pops = []
            for _ in num:
                pops += self.cards.pop()
            return pops
        except IndexError:
            return 'Deck ran out!'

class Graveyard:
    def __init__(self, halfboard):
        self.cards: list[Card] = []
        self.halfboard = halfboard

class Hand:
    def __init__(self, halfboard:'HalfBoard'):
        self.halfboard = halfboard
        self.name = f"{self.halfboard.name}'s hand"
        self.cards: list[Card] = []

class MainZone(Zone):
    def __init__(self, halfboard:'HalfBoard'):
        super().__init__(halfboard)
        self.name = f"{self.halfboard.name}'s Main Zone"

class SubZone(Zone):
    def __init__(self, halfboard):
        super().__init__(halfboard)

    def rename(self):
        self.index = self.halfboard.row.subzones.index(self)
        self.name = f"{self.halfboard.name}'s Sub Zone {self.index}"

class Row:
    def __init__(self, halfboard:'HalfBoard'):
        self.halfboard = halfboard
        self.name = f"{self.halfboard.name}'s Row"
        self.subzones: list[SubZone] = []

class HalfBoard:
    def __init__(self, player_name:str):
        self.name = player_name
        self.deck = Deck(self)
        self.graveyard = Graveyard(self)
        self.main_zone = MainZone(self)
        self.row = Row(self)
        self.hand = Hand(self)
        self.available_actions: list[Action] = []

    @property
    def zones(self):
        return [self.main_zone] + self.row.subzones

    def get_suborder(self):
        return len(self.row.subzones)

    def draw(self, num):
        return Draw(self, num)

class Action:
    def __init__(self, name, board:'Board'):
        self.name = name
        self.board = board
        self.check: Callable[..., bool]|bool = True
        self.trigger: Callable[..., bool]|bool|None = None

    def declare(self):
        #check initial condition
        if self.board.is_available(self):
            self.process()
        else:
            return False
        
    def process(self):
        # After doing something
        self.board.check_trigger()

class Draw(Action):
    def __init__(self, halfboard:HalfBoard, num):
        self.halfboard = halfboard
        self.num = num

    def declare(self):
        super().declare()

    def process(self):
        for _ in range(self.num):
            self.halfboard.hand.cards.append(self.halfboard.deck.pop())
        super().process()

class Attack(Action):
    pass

class Activate(Action):
    pass

class Let(Action):
    def __init__(self, card:Card, zone:Zone, came_from:Zone|Hand|Graveyard, board:'Board'):
        self.card = card
        self.board = board
        self.zone = zone
        self.came_from = came_from

    def declare(self):
        if self.board == self.came_from:
            self.check = False
        super().declare()


    def process(self):
        #if check_condition:
        self.zone.cards.append(self.card)
        #self.came_from.cards.remove(self.card)
        super().process()


class Board:
    def __init__(self, player1:HalfBoard, player2:HalfBoard):
        self.player1 = player1
        self.player2 = player2
        self.players = [player1, player2]
        self.loser = False
        self.current_player: HalfBoard = player1
        self.turn = [0, 0]
        self.state = 'Init'

        self.holding = None
        self.holding_from = None
        self.gamecomponents: list[HalfBoard|Deck|Graveyard|Zone|Hand|Card] = []

    def opponent(self, player:HalfBoard|None=None) -> HalfBoard:
        if player == self.player1:
            return self.player2
        elif player == self.player2:
            return self.player1
        elif player == None:
            return self.opponent(self.current_player)
        else:
            raise ValueError

    def refresh_gamecomponents(self):
        self.gamecomponents = []
        for player in self.players:
            self.gamecomponents.append(player)
            self.gamecomponents.append(player.deck)
            self.gamecomponents.append(player.hand)
            self.gamecomponents.append(player.graveyard)
            if len(player.graveyard.cards) > 0:
                self.gamecomponents.append(player.graveyard.cards[0])
            for zone in player.zones:
                self.gamecomponents.append(zone)
                for card in zone.cards:
                    self.gamecomponents.append(card)

    def refresh_available_actions(self):
        self.refresh_gamecomponents()
        for player in self.players:
            for component in self.gamecomponents:
                player.available_actions.append(component, self.current_player)

    def get_processing_order(self):
        cards: list[Card] = []
        for player in [self.opponent(self.current_turn), self.current_turn]:
            if player.main_zone.cards != []:
                cards.append(player.main_zone.cards[0])
            for zone in player.row.subzones:
                cards.append(zone.cards[0])
            if player.main_zone.cards != []:
                cards.append(player.graveyard.cards[0])
        return cards
    
    def make_checklist(self):
        self.refresh_gamecomponents()
        checklist: list[Callable[..., bool]] = []
        for component in self.gamecomponents:
            if hasattr(component, 'check'):
                checklist.append(component.check)
        return checklist
    
    def make_triggerlist(self):
        self.refresh_gamecomponents()
        triggerlist: list[Callable[..., bool]] = []
        for component in self.gamecomponents:
            if hasattr(component, 'trigger'):
                triggerlist.append(component.trigger)
        return triggerlist
    
    def is_available(self, action:Action):
        ans = True
        for check in self.make_checklist():
            ans *= check(self, action)
            if not ans:
                break
        return ans
    
    def check_trigger(self):
        for trigger in self.make_triggerlist():
            trigger(self)

    def initial_setting(self):
        for player in self.players:
            player.draw(5)
            self.check_trigger(self)

    def interpret(self, type:Literal['click', 'drop'], key:Zone|Deck|Hand|Graveyard, card=None, subzone_num:int|None=None):
        if card == True:
            card = '1'

        if type == 'click':
            self.holding_from = key
            self.holding = key.cards.pop()
            
        elif type == 'drop':
            if key == 'end':
                self.current_player = self.opponent()
                return True
            elif isinstance(key, Zone):
                Let(card, key, self.holding_from, self).declare()
                return True
            elif key == 'temp zone':
                if len(self.current_player.row.subzones) > 4:
                    return 'too many sub zones!'
                else:
                    self.current_player.row.subzones.insert(subzone_num - 1, SubZone(self.current_player))
                    for subzone in self.current_player.row.subzones:
                        subzone.rename()
                    self.current_player.row.subzones[subzone_num - 1].cards.append('l')
                    return True
            elif key == 'end':
                self.current_player = self.opponent()
                return True

    def play(self):
        for i in range(10):
            self.player1.deck.cards.append(i)

        self.player1.row.subzones.append(SubZone(self.player1))
        for subzone in self.player1.row.subzones:
            subzone.rename()
        self.player1.main_zone.cards.append('main card')
        self.player1.row.subzones[0].cards.append('sub card')
        while True:
            #yield True
            print('start loop')
            args: list[str, ] = yield
            print('got message')
            if args != None:
                yield self.interpret(*args)
            else:
                yield 'a'
            print('end loop')

        print(f'game end! {self.opponent(self.loser)} survives.')


#input player 1, 2 {name, deck, etc}
#player1 = HalfBoard('Player 1')
#player2 = HalfBoard('Player 2')
#game = Board(player1, player2)

#game.play()