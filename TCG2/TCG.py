from typing import Literal, Generator, Sequence
from random import shuffle

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
    _name = 'BoundComponent'

    def __init__(self, bind_to:GameComponent, name:str|None=None) -> None:
        self.bind_to = bind_to
        if name:
            self._name = name

    @property
    def name(self):
        return self._name

    @property
    def board(self):
        return self.bind_to.board

class Effect(BoundComponent):
    _name = 'Effect'

    def __init__(self, bind_to: GameComponent, name:str|None=None) -> None:
        super().__init__(bind_to, name)
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
        if self.in_que():
            self.board.event_que.remove(self)
    
    # region    Conditions
    def basic_condition(self):
        '''is_active and current_turn'''
        return self.is_active() and self.current_turn()
    
    def in_que(self):
        return True if self in self.board.event_que else False

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
    def __init__(self, bind_to: GameComponent) -> None:
        super().__init__(bind_to)
        self.triggered: bool = False

    def trigger(self, phase:Literal['Start']|None=None) -> bool:
        raise NotImplementedError
    
    def initialize(self):
        self.triggered = False
        super().initialize()

class ChainEffect(TriggerEffect):
    pass

class Choice:
    typ: Literal['Click', 'Drag', 'Button']

    def __init__(self, effect: Effect, typ:Literal['Click', 'Drag', 'Button'], target_typ:Literal['Location', 'Locations', 'Card', 'Cards'],
                 drops:Sequence[GameComponent], clicks:Sequence[GameComponent]|None=None) -> None:
        self.effect = effect
        self.typ = typ
        self.target_typ = target_typ
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

        self.selected = None

    @property
    def name(self):
        return f"{self.effect.name}'s {self.typ} {self.target_typ} choice"

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
                self.selected = matching_clicks.pop()
            elif self.typ == 'Button':
                self.selected = matching_drops.pop()
        
        if self.selected:
            if self.target_typ == 'Card' and isinstance(self.selected, Card):
                pass
            elif self.target_typ == 'Location' and not isinstance(self.selected, Card):
                pass
            else:
                return False
            print(f'{self.selected.name} selected in {self.name}')
            return True
        else:
            return False

class Button(GameComponent, BoundComponent):
    _name = 'Button'

    def __init__(self, image, bind_to:GameComponent) -> None:
        self.bind_to = bind_to
        self.image = image

class Actions:
    @staticmethod
    def move(card:'Card', location:'Zone|Pack'):
        card.location = location

    @staticmethod
    def destroy(card:'Card'):
        if isinstance(card.location, Graveyard):
            raise NeutralizedException
        else:
            Actions.move(card, card.owner.graveyard)

    @staticmethod
    def burst(player:'HalfBoard'):
        player.has_burst_chance = False
        player.board.in_burst = True

    @staticmethod
    def shuffle(deck:'Deck'):
        shuffle(deck.cards)

class Card(GameComponent):
    def __init__(self, owner:'HalfBoard', name:str, color:Literal['R', 'Y', 'B']|None, power=None,
                 time:Literal[1, 2, 3, 4]|None=None, image=None, description=None):
        super().__init__(owner)
        self.owner = owner
        self._name = name
        self._color = color
        self._power:int|None = power
        self._location: 'Zone|Pack' = self.owner.deck
        self._image = image
        self._description = description
        self._time:int|None = time
        self._time_modifier:int = 0

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
    def time(self):
        if isinstance(self.location, Zone):
            if not self._time:
                return None
            
            time = self._time + self._time_modifier
            if time > 4:
                raise GameException('Time larger than 4!')
            else:
                return time
        else:
            return None
        
    @time.setter
    def time(self, value:int):
        if not self._time:
            raise GameException
        
        if value > 4:
            self._time_modifier = 4 - self._time
        else:
            self._time_modifier = value - self._time

    @property
    def image(self):
        return self._image if self.is_active else None
    
    @property
    def description(self):
        return self._description if self.is_active else None

    @property
    def is_active(self):
        if isinstance(self.location, Zone) or isinstance(self.location, Hand):
            return True
        elif isinstance(self.location, Deck):
            return False
        elif isinstance(self.location, Graveyard):
            return True if self.location.top() is self else False

    def initialize(self):
        self.time_modifier = 0
        if isinstance(self.location, Zone) and self._time:
            self.time = self._time

class Creature(Card):
    def __init__(self, owner:'HalfBoard', name:str, color:Literal['R', 'Y', 'B']|None, power:int,
                 time:Literal[1, 2, 3, 4], image=None, description=None):
        super().__init__(owner, name, color, power, time, image, description)

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
        card.initialize()

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
                if isinstance(self.bind_to, SubZone) and not self.board.in_burst:
                    Actions.burst(self.bind_to.halfboard)
                    return True
                Actions.move(self.card, self.bind_to)
                self.initialize()
                return False
            
            elif self.choice and isinstance(self.choice.selected, Card):
                self.card = self.choice.selected
                self.choice = None
                return True
            
            elif isinstance(self.bind_to, SubZone) and not self.bind_to.halfboard.has_burst_chance:
                self.choice = None
                return False
            
            else:
                self.choice = Choice(self, 'Drag', 'Card', [self.bind_to], self.get_lettable_cards())
                return False
            
        def initialize(self):
            self.card = None
            super().initialize()
            
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
            self.card.initialize()

    def empty(self):
        self.card = None

class MainZone(Zone):
    pass

class SubZone(Zone):
    class Let(Zone.Let):
        card:Card|None=None
        bind_to: 'SubZone'

        def process(self):
            if not self.basic_condition() or not (self.board.in_burst or self.bind_to.halfboard.has_burst_chance):
                self.initialize()
                return False
            
            if self.is_running() and self.card and self.card.location is self.bind_to.halfboard.hand:
                if not self.board.in_burst:
                    Actions.burst(self.bind_to.halfboard)
                    return True
                Actions.move(self.card, self.bind_to)
                self.initialize()
                return False
            
            elif self.choice and isinstance(self.choice.selected, Card):
                self.card = self.choice.selected
                self.choice = None
                return True

            else:
                self.choice = Choice(self, 'Drag', 'Card', [self.bind_to], self.get_lettable_cards())
                return False

class Deck(Pack):
    class Draw(Effect):
        selected: bool = False
        bind_to: 'Deck'

        def process(self):
            if not self.basic_condition():
                self.initialize()
                return False

            if self.is_running() and self.selected is True:
                try:
                    Actions.move(self.bind_to.top(), self.bind_to.halfboard.hand)
                    self.board.in_burst = False
                    self.bind_to.halfboard.has_burst_chance = False
                    self.initialize()
                    return False
                
                except NoCardException:
                    self.board.loser = self.bind_to.halfboard
                    raise EndException
            
            elif self.choice and self.choice.selected:
                self.selected = True
                self.choice = None
                return True

            elif self.bind_to.halfboard.has_burst_chance:
                self.choice = Choice(self, 'Click', 'Location', [self.bind_to])
                return False
            
            else:
                self.initialize()
                return False
            
        def initialize(self):
            self.selected = False
            super().initialize()
        
    def __init__(self, halfboard: 'HalfBoard') -> None:
        super().__init__(halfboard)
        self.effects = [self.Draw(self)]

    def top(self):
        try:
            return self.cards[0]
        except IndexError:
            raise NoCardException
        
    def append(self, card: Card):
        super().append(card)

class Graveyard(Pack):
    def top(self):
        try:
            return self.cards[0]
        except IndexError:
            return None
        
    def append(self, card: Card):
        super().append(card)

class Hand(Pack):
    def __init__(self, halfboard:'HalfBoard') -> None:
        super().__init__(halfboard)

class HalfBoard(GameComponent):
    class Decay(TriggerEffect):
        bind_to: 'HalfBoard'
        zones: list[Zone]|None = None

        def trigger(self, phase) -> bool:
            if not self.in_que() and isinstance(self.board.running, Deck.Draw) and self.bind_to is self.board.current_player:
                return True
            else:
                return False
            
        def process(self) -> bool:
            if self.is_running():
                if not self.zones:
                    self.zones = [zone for zone in self.bind_to.zones]
                
                while self.zones:
                    zone = self.zones.pop(0)
                    if zone.card and zone.card.time:
                        zone.card.time -= 1
                        return True

                self.initialize()
                return False
            else:
                self.initialize()
                return False

        def initialize(self):
            self.zones = None
            super().initialize()

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
        self.effects = [self.Decay(self)]

        self._bursted:bool = False
        self.has_burst_chance:bool = False

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
    class BurstEnd(ChainEffect):
        bind_to: 'Board'
        def trigger(self, phase):
            if not self.in_que() and isinstance(self.board.running, Deck.Draw) and self.board.in_burst:
                return True
            else:
                return False
        
        def process(self):
            if self.is_running():
                for subzone in [subzone for player in self.bind_to.players for subzone in player.subzones]:
                    if subzone.card:
                        Actions.destroy(subzone.card)
                        return True
                self.board.in_burst = False
                self.initialize()
                return False
            else:
                return False
    
    def __init__(self, player1:HalfBoard, player2:HalfBoard) -> None:
        self.effects = [self.BurstEnd(self)]

        self.player1 = player1
        self.player2 = player2
        self.player1._parent = self
        self.player2._parent = self

        self.holding:Card|Button|None = None
        self.loser: HalfBoard|None = None
        self.turn:int = 0   # odd for 1, even for 2
        self.in_burst:bool = False

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

    def check_trigger_effects(self, phase:Literal['Start']|None=None):
        chains = []
        for gc in self.gamecomponents:
            for trigger_effect in [eff for eff in gc.effects if isinstance(eff, TriggerEffect)]:
                if trigger_effect.trigger(phase):
                    if isinstance(trigger_effect, ChainEffect):
                        chains.append(trigger_effect)
                    else:
                        self.event_que.append(trigger_effect)
        self.event_que = chains + self.event_que

    def play(self):
        try:
            #Init
            for player in self.players:
                Actions.shuffle(player.deck)
                for _ in range(5):
                    try:
                        Actions.move(player.deck.top(), player.hand)
                    except NoCardException:
                        self.loser = player
                        raise EndException
            
            while True:
                #Turn Start
                self.turn += 1
                self.current_player.has_burst_chance = True
                self.check_trigger_effects('Start')

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
                                raise GameException('input loop break without appropriate input!')
                        self.active_choices.clear()
                    # Automatic
                    while self.event_que:
                        self.running = self.event_que[0]
                        self.check_trigger_effects()
                        if self.event_que[0] is self.running:
                            while self.running.process():
                                if self.running and self.running.choice:
                                    yield
                        else:
                            continue
                    
                    self.running = None

        except EndException as end:
            raise end

    def IO(self) -> Generator['EndException|None', tuple[Literal['click', 'drop', 'rightclick'], list[GameComponent]], None]:
        try:
            while True:
                result = next(self.game)
                print('waiting for the message...')

                while not self.selected_choice:
                    print(f"Choices: {[choice.name for choice in self.active_choices]}")
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

        except EndException as end:
            yield end

class GameException(Exception):
    pass

class EndException(GameException):
    pass

class NoCardException(GameException):
    pass

class NeutralizedException(GameException):
    pass
