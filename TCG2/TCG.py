from typing import Literal, Generator, Sequence, Callable
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
        self.event:'Event|None' = None
        self._gen:Generator|None = None
        self.activated = False

    def is_running(self):
        return True if self.board and self.board.running is self else False

    def gen(self) -> Generator["Choice|Event|None", None, None]:
        yield

    def process(self):
        '''Set self.event/choice.'''
        if not self._gen:
            self._gen = self.gen()
        try:
            result = next(self._gen)
            if isinstance(result, Event):
                self.event = result
            elif isinstance(result, Choice):
                self.choice = result
        except StopIteration:
            self.initialize()

    def initialize(self):
        self.choice = None
        self.event = None
        self.activated = False
        self._gen = self.gen()
    
    # region    Conditions
    def basic_condition(self):
        '''is_active and current_turn'''
        return self.is_active() and self.current_turn()
    
    def in_que(self):
        return True if self in self.board.effect_que else False   

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

class StaticEffect(Effect):
    target_type: list[Literal['Power', 'Time', 'Color', 'Cost']] = []

    def __init__(self, bind_to:GameComponent, target_type:list[Literal['Power', 'Time', 'Color', 'Cost']], name:str|None=None) -> None:
        super().__init__(bind_to, name)
        self.target_type = target_type
    
    def check(self):
        return None

class CommandEffect(Effect):
    pass

class TriggerEffect(Effect):
    def trigger(self, timing:Literal['before', 'after'], event) -> Effect|None:
        raise NotImplementedError

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

class Event:
    _board: 'Board|None' = None

    def __init__(self, effect:Effect|None, board:'Board|None'=None) -> None:
        if effect:
            self.effect = effect
        elif board:
            self._board = board
        else:
            raise Exception
        
        self.done:bool=False

    @property
    def board(self):
        if self._board:
            return self._board
        else:
            return self.effect.board
        
    def _run(self):
        raise NotImplementedError

    def run(self):
        '''self.done = True'''
        try:
            self._run()
        except GameException as e:
            raise e
        self.done = True

# region Events
class Move(Event):
    card:'Card'
    location:'Zone|Pack'

    def __init__(self, effect:Effect|None, card, location) -> None:
        if effect:
            super().__init__(effect)
        self.card = card
        self.location = location

    def _run(self):
        self.card.location = self.location

class Destroy(Move):
    card:'Card'

    def __init__(self, effect, card:'Card') -> None:
        super().__init__(effect, card, card.owner.graveyard)
        self.card = card

    def _run(self):
        if isinstance(self.card.location, Graveyard):
            raise NeutralizedException
        else:
            Move(self.effect, self.card, self.location).run()

class Burst(Event):
    player:'HalfBoard'

    def __init__(self, effect, player) -> None:
        super().__init__(effect)
        self.player = player
    
    def _run(self):
        self.player.has_burst_chance = False
        self.player.board.in_burst = True

class Shuffle(Event):
    deck:'Deck'
        
    def __init__(self, effect:Effect, deck) -> None:
        super().__init__(effect)
        self.deck = deck

    def _run(self):
        shuffle(self.deck.cards)

class ChangeValue(Event):
    def __init__(self, effect:Effect|None, card:'Card', value:Literal['time', 'power'], modifier:int, board:'Board|None'=None) -> None:
        super().__init__(effect, board)
        self.card = card
        self.value = value
        self.modifier = modifier

    def _run(self):
        if self.value == 'time':
            self.card._time_modifier += self.modifier
        elif self.value == 'power':
            self.card._power_modifier += self.modifier

class Start_Turn(Event):
    def _run(self):
        self.board.turn += 1
        self.board.current_player.has_burst_chance = True
# endregion

class Card(GameComponent):
    def __init__(self, owner:'HalfBoard', name:str, color:Literal['R', 'Y', 'B']|None, power=None,
                 cost:dict[Literal['R', 'Y', 'B'], int]=dict(),
                 time:Literal[1, 2, 3, 4]|None=None, image=None, description=None):
        super().__init__(owner)
        self.owner = owner
        self._name = name
        self._color = color
        self._power:int|None = power
        self._power_modifier:int = 0
        self._cost:dict[Literal['R', 'Y', 'B'], int] = cost
        self._cost_modifier:dict[Literal['R', 'Y', 'B'], int] = {}
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
        return self._power + self._power_modifier if self._power and self.is_active else None

    @property
    def cost(self):
        return {k: self._cost[k] + self._cost_modifier[k] for k in self._cost} if self._cost and self.is_active else None

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
                 time:Literal[1, 2, 3, 4], cost:dict[Literal['R', 'Y', 'B'], int]=dict(),
                 image=None, description=None):
        super().__init__(owner, name, color, power, cost, time, image, description)

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
    class Let(CommandEffect):
        card:Card|None=None
        bind_to: 'Zone'

        def gen(self):
            while True:
                if not self.basic_condition() or self.bind_to.card:
                    return None
                
                if not (self.choice and isinstance(self.choice.selected, Card)):
                    self.choice = Choice(self, 'Drag', 'Card', [self.bind_to], self.get_lettable_cards())
                    yield self.choice
                    if isinstance(self.choice.selected, Card) and self.choice.selected.location is self.bind_to.halfboard.hand:
                        break
            
            self.card = self.choice.selected
            self.choice = None
            self.activated = True
            yield
            
            while True:
                if not self.basic_condition() or self.bind_to.card:
                    return None
                    
                yield Move(self, self.card, self.bind_to)
                if self.event and self.event.done:
                    return None
                        
        def initialize(self):
            self.card = None
            super().initialize()
            
        def get_lettable_cards(self):
            lettable_cards: list[Card] = []
            for card in self.bind_to.halfboard.hand.cards:
                if not card.cost or self.able_to_pay_cost(card.cost):
                    lettable_cards.append(card)
            return lettable_cards
        
        def able_to_pay_cost(self, cost:dict):
            for color in cost.keys():
                if cost[color] > self.bind_to.halfboard.total_mana[color]:
                    return False
            return True

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

        def gen(self):
            while True:
                if not self.basic_condition() or self.bind_to.card or not (self.board.in_burst or self.bind_to.halfboard.has_burst_chance):
                    return None
                
                yield Choice(self, 'Drag', 'Card', [self.bind_to], self.get_lettable_cards())
                if self.choice and isinstance(self.choice.selected, Card) and self.choice.selected.location is self.bind_to.halfboard.hand:
                    break
            
            self.card = self.choice.selected
            self.choice = None
            self.activated = True
            yield
            
            while True:
                if not self.basic_condition() or self.bind_to.card:
                    return None
                    
                if not self.board.in_burst:
                    if self.bind_to.halfboard.has_burst_chance:
                        yield Burst(self, self.bind_to.halfboard)
                    else:
                        return None
                
                else:
                    yield Move(self, self.card, self.bind_to)
                    if self.event and self.event.done:
                        return None

        def check_validity(self):
            if not self.basic_condition() or self.bind_to.card:
                self.initialize()
                return False
            else:
                return True

class Deck(Pack):
    class Draw(CommandEffect):
        selected: bool = False
        bind_to: 'Deck'

        def gen(self):
            while True:
                if not self.basic_condition():
                    return None
                
                elif self.bind_to.halfboard.has_burst_chance:
                    yield Choice(self, 'Click', 'Location', [self.bind_to])
                    if self.choice and self.choice.selected:
                        break

                else:
                    self.choice = None
                    yield

            self.choice = None
            self.activated = True
            yield

            while True:
                if not self.basic_condition():
                    return None
                
                try:
                    yield Move(self, self.bind_to.top(), self.bind_to.halfboard.hand)
                    if self.event and self.event.done:
                        break
                
                except NoCardException:
                    self.board.loser = self.bind_to.halfboard
                    raise EndException
                
            self.board.in_burst = False
            self.bind_to.halfboard.has_burst_chance = False
            return None
            
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

        def trigger(self, timing, event):
            if timing == 'after' and isinstance(self.board.running, Deck.Draw) and self.bind_to is self.board.current_player:
                self.activated = True
            else:
                self.activated = False
            
        def gen(self):
            if not self.zones:
                self.zones = [zone for zone in self.bind_to.zones if zone.card]
            while self.zones:
                if self.event and self.event.done:
                    self.event = None
                    yield
                
                elif self.is_running():
                    zone = self.zones.pop(0)
                    if zone.card:
                        if zone.card.time is not None:
                            yield ChangeValue(self, zone.card, 'time', -1)
                        else:
                            yield Destroy(self, zone.card)
                else:
                    yield
            
            return None

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

    @property
    def total_mana(self):
        total_mana:dict[Literal['R', 'Y', 'B'], int] = {
            'R': 0,
            'Y': 0,
            'B': 0
        }
        for card in [zone.card for zone in self.zones if zone.card]:
            for key in total_mana.keys():
                if key == card.color:
                    total_mana[key] += 1
                if card.cost and card.cost[key] != 0:
                    total_mana[key] += card.cost[key]
        return total_mana

class Board(GameComponent):
    class BurstEnd(TriggerEffect):
        bind_to: 'Board'
        def trigger(self, timing, event):
            if timing == 'after' and isinstance(self.board.running, Deck.Draw) and self.board.in_burst:
                self.activated = True
            else:
                self.activated = False
        
        def gen(self):
            for subzone in [subzone for player in self.bind_to.players for subzone in player.subzones]:
                if subzone.card:
                    yield Destroy(self, subzone.card)
            self.board.in_burst = False
            return None
    
    class CardDecayFactory(TriggerEffect):
        class CardDecay(Effect):
            bind_to:'Board'
            def __init__(self, bind_to: GameComponent, card:Card, name:str|None=None) -> None:
                super().__init__(bind_to, name)
                self.card = card
                self.activated = True

            def gen(self):
                while not self.card.time and isinstance(self.card.location, Zone):
                    yield Destroy(self, self.card)
                return None
        
        bind_to:'Board'
        def trigger(self, timing: Literal['before']|Literal['after'], event:Event) -> Effect|None:
            if timing == 'before':
                return None

            for gc in self.bind_to.gamecomponents:
                if isinstance(gc, Card) and gc.time is not None and gc.time <= 0:
                    return self.CardDecay(self.bind_to, gc)

    class TurnStartEffect(Effect):
        def __init__(self, bind_to: GameComponent) -> None:
            super().__init__(bind_to)

        def gen(self):
            print('Attempt to change Turn...')
            self.activated = True
            yield
            yield Start_Turn(self)
            print('Turn ended.')
            return None

    def __init__(self, player1:HalfBoard, player2:HalfBoard) -> None:
        self.effects = [self.BurstEnd(self), self.CardDecayFactory(self)]

        self.player1 = player1
        self.player2 = player2
        self.player1._parent = self
        self.player2._parent = self

        self.holding:Card|Button|None = None
        self.loser: HalfBoard|None = None
        self.turn:int = 0   # odd for 1, even for 2
        self.in_burst:bool = False

        self.running: Effect|None = None
        self.effect_que: list[Effect] = []
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
            for effect in [eff for eff in gc.effects if not isinstance(eff, TriggerEffect)]:
                effect.initialize()
                effect.process()
                if effect.activated:
                    self.effect_que.append(effect)
                elif effect.choice:
                    self.active_choices.append(effect.choice)

        if self.effect_que:
            self.active_choices = []

    def check_trigger_effects(self, timing:Literal['before', 'after'], event):
        chains = []
        for gc in self.gamecomponents:
            for effect in [eff for eff in gc.effects if not isinstance(eff, CommandEffect) and not eff.in_que()]:
                if isinstance(effect, TriggerEffect):
                    new_effect = effect.trigger(timing, event)
                    if new_effect:
                        if timing == 'before':
                            chains.append(new_effect)
                        else:
                            self.effect_que.append(new_effect)
                    elif effect.activated:
                        if timing == 'before':
                            chains.append(effect)
                        else:
                            self.effect_que.append(effect)
                elif isinstance(effect, StaticEffect) and effect.check():
                    self.effect_que.append(effect)

        self.effect_que = chains + self.effect_que

    def play(self):
        try:
            #Init
            for player in self.players:
                shuffle(player.deck.cards)
                for _ in range(5):
                    try:
                        Move(None, player.deck.top(), player.hand).run()
                    except NoCardException:
                        self.loser = player
                        raise EndException
                    
            while True:
                #Turn Start
                turn_start = self.TurnStartEffect(self)
                turn_start.process()    # activates
                self.effect_que.append(turn_start)

                # Power check
                while self.current_player.total_power <= self.opponent().total_power or turn_start.activated:

                    # Manual
                    if not self.effect_que:
                        print('Empty que. Try Idle search...')
                        self.check_idle_effects()
                        while not self.effect_que:
                            yield
                            if self.selected_choice:
                                self.selected_choice.effect.process()
                                if self.selected_choice.effect.activated:
                                    self.effect_que.append(self.selected_choice.effect)
                                self.selected_choice = None
                            else:
                                raise GameException('input loop break without appropriate input!')
                        self.active_choices.clear()
                    
                    # Automatic
                    while self.effect_que:
                        print(f'effect que: {self.effect_que}')
                        self.running = self.effect_que[0]
                        print(f'running {self.running}...')
                        self.running.process()

                        if self.running.event:
                            self.check_trigger_effects('before', self.running.event)
                            if self.running == self.effect_que[0]:
                                print(f'running {self.running.event}!')
                                self.running.event.run()
                                self.check_trigger_effects('after', self.running.event)
                                self.running.process()
                            
                        elif self.running.choice:
                            yield
                            
                        if not self.running.activated:
                            self.effect_que.remove(self.running)

                    self.running = None

        except EndException as end:
            raise end

    def IO(self) -> Generator['EndException|None', tuple[Literal['click', 'drop', 'rightclick'], list[GameComponent]], None]:
        try:
            while True:
                result = next(self.game)
                print('game needs input...')

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
