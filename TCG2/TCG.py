from typing import Literal, Generator, Sequence

class GameComponent:
    _name: str = 'GameComponent'
    effects: list['Effect'] = []
    
    def __init__(self, parent:'GameComponent', name:str|None=None) -> None:
        self._parent = parent
        if name:
            self._name = name
    
    @property
    def name(self):
        return self._name
    
    @property
    def halfboard(self) -> 'HalfBoard':
        return self._parent.halfboard
    
    @property
    def board(self) -> 'Board':
        return self._parent.board
        
class BoundComponent:
    bind_to: GameComponent

    def __init__(self, bind_to:GameComponent) -> None:
        self.bind_to = bind_to

    @property
    def board(self):
        return self.bind_to.board

class Effect(BoundComponent):
    def __init__(self, bind_to: GameComponent) -> None:
        super().__init__(bind_to)
        self.choice:'Choice|None' = None

    def is_running(self):
        return True if self.board and self.board.running is self else False

    def process(self) -> bool:
        '''
        True: activated. must be added to the que.\n
        False: not activated.
        '''
        print(f'processing {self}!')
        return False
    
    def initialize(self):
        self.choice = None
        if self.is_running():
            self.board.running = None
    
    # region    Conditions
    def basic_condition(self):
        '''is_active and current_turn'''
        return self.is_active() and self.current_turn()
    
    def is_active(self):
        if isinstance(self.bind_to, Card):
            return True if self.bind_to.is_active else False
        else:
            return True
        
    def current_turn(self):
        if isinstance(self.bind_to, Card):
            return True if self.bind_to.owner is self.board.current_player else False
        else:
            return True if self.bind_to.halfboard is self.board.current_player else False
    # endregion

class TriggerEffect(Effect):
    def trigger(self) -> bool:
        raise NotImplementedError

class Choice:
    typ: Literal['Click', 'Drag', 'Button']

    def __init__(self, effect: Effect, typ:Literal['Click', 'Drag', 'Button'],
                 drops:Sequence[GameComponent], clicks:Sequence[GameComponent]|None=None) -> None:
        self.effect = effect
        self.typ = typ
        self.drops = drops
        if typ == 'Click':
            if clicks:
                raise Exception('Click Choice does not need clicks list!')
            else:
                self.clicks = self.drops
        elif typ == 'Drag':
            if clicks is None:
                raise Exception('Drag Choice needs its original location!')
            else:
                self.clicks = clicks
        elif typ == 'Button':
            if not clicks:
                raise Exception('Button Choice does not have a Button to click!')
            else:
                self.clicks = clicks
        else:
            raise Exception('Not a right Choice type!')

        self.selected = []

    def match(self, input_click:Sequence[GameComponent], input_drop:Sequence[GameComponent]):
        matching_clicks = set(input_click) & set(self.clicks)
        if not matching_clicks:
            return False
        
        if self.typ == 'Click':
            self.selected = matching_clicks.pop()
        else:
            matching_drops = set(input_drop) & set(self.drops)
            if not matching_drops:
                return False
            if self.typ == 'Drag':
                self.selected = [matching_clicks, matching_drops]
            elif self.typ == 'Button':
                self.selected = matching_drops
        if self.selected:
            print(f'{self.selected}')
        return True if self.selected else False

class Button(GameComponent, BoundComponent):
    def __init__(self, image, bind_to:GameComponent) -> None:
        self.bind_to = bind_to
        self.image = image

class Actions:
    @staticmethod
    def move(card:'Card', location:'Zone|Pack'):
        card.location = location

class Card(GameComponent):
    def __init__(self, owner:'HalfBoard', name:str, color:Literal['R', 'Y', 'B']|None, power=None, image=None, description=None) -> None:
        super().__init__(owner)
        self.owner = owner
        self._name = name
        self._color = color
        self._power:int|None = power
        self._location: 'Zone|Pack' = self.owner.deck
        self._image = image
        self._description = description
        self.time: Literal[1, 2, 3, 4]|None = None

    @property
    def name(self):
        return self._name if self.is_active else None
    
    @property
    def color(self):
        return self._color if self.is_active else None

    @property
    def power(self):
        return self._power if self.is_active else None

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, new_loc:'Pack|Zone'):
        if new_loc is self.location:
            return None
        
        if isinstance(self._location, Pack):
            self._location.remove(self)
        else:
            self._location.empty()
        
        self._location = new_loc

        if isinstance(self._location, Pack):
            self._location.append(self)
        else:
            self._location.add(self)

    @property
    def image(self):
        return self._image if self.is_active else None
    
    @property
    def description(self):
        return self._description if self.is_active else None

    @property
    def is_active(self):
        if isinstance(self.location, Zone):
            return True
        elif isinstance(self.location, Deck) or isinstance(self.location, Hand):
            return False
        elif isinstance(self.location, Graveyard):
            return True if self.location.top() is self else False

class Creature(Card):
    pass

class Spell(Card):
    pass

class Pack(GameComponent):
    def __init__(self, halfboard:'HalfBoard') -> None:
        super().__init__(halfboard)
        self._cards: list[Card] = []    # 0: top

    @property
    def board(self):
        return self.halfboard.board

    @property
    def cards(self):
        return self._cards

    @property
    def length(self):
        return len(self._cards)
    
    def append(self, card:Card):
        self._cards.append(card)

    def remove(self, card:Card):
        self._cards.remove(card)

class Zone(GameComponent):
    class Let(Effect):
        card:Card|None=None
        bind_to: 'Zone'

        def process(self):
            if not self.basic_condition():
                self.initialize()
                return False
            
            if self.is_running() and self.card and self.card.location is self.bind_to.halfboard.hand:
                if isinstance(self.bind_to, SubZone):
                    self.bind_to.halfboard.has_bursted = True
                Actions.move(self.card, self.bind_to)
                
                self.initialize()
                return False
            
            elif self.choice and isinstance(self.choice.selected, Card):
                self.card = self.choice.selected
                self.choice = None
                return True
            
            else:
                self.choice = Choice(self, 'Drag', [self.bind_to], self.get_lettable_cards())
                return False
            
        def get_lettable_cards(self):
            return self.bind_to.halfboard.hand.cards

    def __init__(self, halfboard:'HalfBoard') -> None:
        super().__init__(halfboard)
        self.card:Card|None = None
        self.effects = [self.Let(self)]

    @property
    def gamecomponents(self) -> list[GameComponent]:
        return [self, self.card] if self.card else [self]

    @property
    def board(self):
        return self.halfboard.board

    @property
    def power(self):
        if self.card and self.card.power is not None:
            return self.card.power
        else:
            return 0

    def add(self, card:Card):
        if self.card:
            raise Exception('There is another card in the Zone!')
        else:
            self.card = card

    def empty(self):
        self.card = None

class MainZone(Zone):
    pass

class SubZone(Zone):
    pass

class Deck(Pack):
    class Draw(Effect):
        selected: bool = False
        bind_to: 'Deck'

        def process(self):
            if not self.basic_condition():
                self.initialize()
                return False

            if self.is_running() and self.selected is True:
                drawcard = self.bind_to.top()
                if not drawcard:
                    self.board.loser = self.bind_to.halfboard
                    raise self.board.End
                else:
                    Actions.move(drawcard, self.bind_to.halfboard.hand)
                    self.initialize()
                    return False
            
            elif self.choice and self.choice.selected:
                self.selected = True
                self.choice = None
                return True

            elif not self.bind_to.halfboard.has_bursted:
                self.choice = Choice(self, 'Click', [self.bind_to])
                return False
            
            return False
        
    def __init__(self, halfboard: 'HalfBoard') -> None:
        super().__init__(halfboard)
        self.effects = [self.Draw(self)]

    def top(self):
        try:
            return self.cards[0]
        except IndexError:
            return None

class Graveyard(Pack):
    def top(self):
        try:
            return self.cards[0]
        except IndexError:
            return None

class Hand(Pack):
    def __init__(self, halfboard:'HalfBoard') -> None:
        super().__init__(halfboard)

class HalfBoard(GameComponent):
    class BurstEndEffect(TriggerEffect):
        bind_to: 'HalfBoard'
        def trigger(self):
            return True if isinstance(self.board.running, Deck.Draw) and self.board.bursted else False

    def __init__(self, name:str) -> None:
        self._name = name
        self.deck = Deck(self)
        self.graveyard = Graveyard(self)
        self.hand = Hand(self)
        self.mainzones = [
            MainZone(self),
            MainZone(self),
            MainZone(self)
        ]
        self.subzones = [
            SubZone(self),
            SubZone(self),
            SubZone(self)
        ]
        self.zones = self.mainzones + self.subzones
        self.effects = [self.BurstEndEffect(self)]

        self._bursted:bool = False
        self.has_bursted:bool = False

    @property
    def halfboard(self):
        return self

    @property
    def gamecomponents(self) -> list[GameComponent]:
        gc = [self, self.hand, self.graveyard, self.deck]
        for zone in self.zones:
            gc.extend(zone.gamecomponents)
        return gc

    @property
    def total_power(self):
        return sum([zone.power for zone in self.zones])

class Board(GameComponent):
    class End(Exception):
        pass

    def __init__(self, player1:HalfBoard, player2:HalfBoard) -> None:
        self.player1 = player1
        self.player2 = player2
        self.player1._parent = self
        self.player2._parent = self

        self.holding:Card|Button|None = None
        self.loser: HalfBoard|None = None
        self.turn:int = 0   # odd for 1, even for 2
        self._bursted:bool = False

        self.running: Effect|None = None
        self.event_que: list[Effect] = []
        self.active_choices: list[Choice] = []
        self.selected_choice: Choice|None = None

        self.game = self.play()

    @property
    def board(self):
        return self

    @property
    def halfboard(self):
        raise AttributeError

    @property
    def current_player(self):
        return self.player1 if self.turn%2 else self.player2

    @property
    def players(self):
        return [self.current_player, self.opponent()]
    
    @property
    def gamecomponents(self) -> list[GameComponent]:
        return [self] + self.current_player.gamecomponents + self.opponent().gamecomponents

    @property
    def bursted(self):
        return self._bursted
    
    @bursted.setter
    def bursted(self, boolean:bool):
        if self.bursted is False and boolean is True:
            self._bursted = True
        elif self.bursted is True and boolean is False:
            self._bursted = False
        else:
            return None

    def opponent(self, player:HalfBoard|None=None):
        if player:
            return self.player1 if player is self.player2 else self.player2
        else:
            return self.player2 if self.current_player is self.player1 else self.player1

    def find_holding(self, lst):
        for key in lst:
            if isinstance(key, Button):
                return key
        for key in lst:
            if isinstance(key, Card):
                return key

    def check_idle_effects(self):
        self.active_choices = []
        for gc in self.gamecomponents:
            for idle_effect in [eff for eff in gc.effects if not isinstance(eff, TriggerEffect)]:
                if idle_effect.process():
                    self.event_que.append(idle_effect)
                elif idle_effect.choice:
                    self.active_choices.append(idle_effect.choice)

    def check_trigger_effects(self):
        for gc in self.gamecomponents:
            for trigger_effect in [eff for eff in gc.effects if isinstance(eff, TriggerEffect)]:
                if trigger_effect.trigger():
                    self.event_que.append(trigger_effect)

    def play(self):
        try:
            #Init
            while True:
                #Turn Start
                self.turn += 1
                self.current_player.has_bursted = False
                self.check_trigger_effects()

                # Power check
                while self.current_player.total_power <= self.opponent().total_power:
                    # Manual
                    if not self.event_que:
                        self.check_idle_effects()
                        while not self.event_que:
                            yield
                            if self.selected_choice:
                                if self.selected_choice.effect.process():
                                    self.event_que.append(self.selected_choice.effect)
                                self.selected_choice = None
                            else:
                                raise Exception('input loop break without appropriate input!')
                        self.active_choices.clear()
                    # Automatic
                    while self.event_que:
                        self.running = self.event_que[0]
                        self.check_trigger_effects()
                        if self.event_que[0] is self.running:
                            while self.running:
                                self.running.process()
                                if self.running and self.running.choice:
                                    yield
                            self.event_que.pop(0)
                        else:
                            continue
                    
                    self.running = None

        except self.End:
            yield 'end!'

    def IO(self) -> Generator[Literal['end!']|None, tuple[Literal['click', 'drop', 'rightclick'], list[GameComponent]], None]:
        while not self.loser:
            result = next(self.game)
            if result:
                continue
            else:
                print('waiting for the message...')

            while not self.selected_choice:
                print(f"Choices: {self.active_choices}")
                click = drop = None
                msgtype, msgkeys = yield
                if msgtype != 'click':
                    continue
                else:
                    click = msgkeys
                    self.holding = self.find_holding(msgkeys)
                msgtype, msgkeys = yield
                if msgtype != 'drop':
                    continue
                else:
                    drop = msgkeys
                    self.holding = None
                    
                for choice in self.active_choices:
                    if choice.match(click, drop):
                        self.selected_choice = choice
                        break
                else:
                    print('No matching choice.')

        yield 'end!'
