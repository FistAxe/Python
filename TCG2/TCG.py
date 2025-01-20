from typing import Callable, Literal, Union, List, Any, TypeVar, Generic
from random import shuffle

T = TypeVar("T")

class GameComponent:
    _halfboard: 'HalfBoard'
    effects: list['Effect']
    name: str

    def __init__(self, halfboard:'HalfBoard', name:str|None=None):
        raise Exception("Called Abstract Class!")

    @property
    def halfboard(self):
        if isinstance(self, HalfBoard):
            return self
        elif isinstance(self, Card):
            return self.owner
        else:
            return self._halfboard
        
    @property
    def board(self):
        if isinstance(self, Board):
            print('board.board was called.')
            return self
        elif self.halfboard:
            return self.halfboard.board
        else:
            raise AttributeError('halfboard not initialized!')

    def is_for_current_player(self):
        if self.halfboard.board.current_player == self.halfboard:
            return True
        else:
            return False
    
    # For Packs only
    def is_holded(self):
        '''Checks if clicked and droped on same place'''
        if self.halfboard.board.holding == self:
            return True
        else:
            return False

class Effect():
    '''bind_to, effectblocks, board, is_valid'''
    _name='Effect'

    def __init__(self, bind_to:GameComponent, name:str|None=None):
        self.bind_to = bind_to
        if name:
            self.name = name
        self.choice: Choice|None = None

    def __repr__(self):
        return f"<{self.name} at {hex(id(self))}>"

    @property
    def board(self):
        if self.bind_to:
            return self.bind_to.board
        else:
            raise AttributeError("Tried to load Board from free Effect!")
    
    @property
    def name(self):
        return f"{self.bind_to.name}'s {self._name}"
    
    @name.setter
    def name(self, name:str):
        self._name = name

    def is_valid(self):
        '''카드: 드러남 SubZone: 존재함 이외: 항상'''
        if self.bind_to:
            if isinstance(self.bind_to, Card):
                if self.bind_to.reveal_type():
                    return True
            elif isinstance(self.bind_to, SubZone):
                try:
                    return bool(self.bind_to.row)
                except Exception:
                    pass
            else:
                return True
            self.current_eb = None
            return False
        else:
            print(f'Effect {self} has no bind_to! Delete.')
            del self
            return False

    def valid_property(self, var:T) -> T|None:
        return var if self.is_valid() else None

    def execute(self, in_event: 'Choice|Action|None') -> 'Choice|Action|None':
        event = self._execute(in_event)
        if isinstance(event, Choice):
            self.choice = event
        else:
            self.choice = None
        return event
    
    def _execute(self, in_event: 'Choice|Action|None') -> 'Choice|Action|None':
        '''
        if self.chosen(in_event):
            event = Action
        elif Condition:
            event = Choice
        return self.give_event(event)
        '''
        raise NotImplementedError

    def chosen(self, in_event:'Event|None') -> bool:
        return bool(self.choice and self.choice == in_event)

'''EffectBlocks'''
class Condition:
    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

class Event:
    name: str = 'Dummy Event'
    def __init__(self, effect:Effect|None, name:str|None=None, identifier:int|None=None) -> None:
        self.effect = effect
        if name:
            self.name = name
        if identifier is not None:
            self.identifier = identifier

    def __repr__(self):
        return f"<{self.name} {'by ' + self.effect.name if self.effect else ''} at {hex(id(self))}>"

    def is_valid(self):
        if self.effect:
            return self.effect.is_valid()
        else:
            return True

class GiveCardEvent(Event):
    card:'Card'

class GivePlaceEvent(Event):
    place:'Pack'

class Restriction(Event):
    def verify(self, event:Event) -> bool:
        return True

class Choice(Event):
    effect: Effect
    image: str|None = None
    is_button: bool = False
    name = 'Dummy Choice'
    def __init__(self, effect: Effect, key:list[GameComponent]|GameComponent|Literal['temp zone']|'Choice'|None=None,
                 chooser:Literal['self', 'opponent']='self', name:str|None=None, identifier:int|None=None):
        super().__init__(effect, name, identifier)
        self.chooser = self.effect.bind_to.halfboard if chooser == 'self' else self.effect.board.opponent(self.effect.bind_to.halfboard)

        if key:
            self._key = key
        else:
            self._key = self.effect.bind_to

    @property
    def key(self):
        if self.effect.is_valid():
            return self._key
        else:
            return None

    def match(self, key:'GameComponent|str|Choice|None', index:int|None) -> bool:
        '''key와 self.key 비교'''
        if self.key == key:
            return True
        else:
            return False

    def clicked(self):
        return True if self.effect.board.holding == self else False

class ButtonChoice(Choice):
    def __init__(self, effect: Effect, image:str|None=None, chooser:Literal['self', 'opponent']='self', name:str|None=None, identifier:int|None=None):
        super().__init__(effect, key=self, chooser=chooser, name=name, identifier=identifier)
        self.is_button = True
        self.image = image

class SelectCardChoice(Choice, GiveCardEvent):
    def __init__(self, effect:Effect, key:list['Card'], image:str|None=None, chooser:Literal['self', 'opponent']='self', name:str|None=None, identifier:int|None=None):
        super().__init__(effect, None, chooser, name, identifier)
        self.image = image
        self._key = key

class SelectPlaceChoice(Choice, GivePlaceEvent):
    def __init__(self, effect:Effect, key:list['Pack'], image:str|None=None, chooser: Literal['self', 'opponent']='self', name:str|None=None, identifier:int|None=None):
        super().__init__(effect, None, chooser, name, identifier)
        self.image = image
        self._key = key

    @property
    def key(self):
        if self.effect.is_valid():
            return self._key
        else:
            return None

    def match(self, key:'GameComponent|str|Choice|None', index:int|None) -> bool:
        if self.key and key in self.key:
            self.place = key
            return True
        else:
            return False

class Action(Event):
    _state: Literal['pending', 'processing']|None = None

    def __init__(self, effect: Effect | None, name:str, identifier:int|None=None, **kwargs) -> None:
        super().__init__(effect, name, identifier)

    @property
    def state(self):
        return self._state
    
    @state.setter
    def state(self, string:Literal['pending', 'processing', 'resolved']):
        if string == 'pending':
            self._state = string
        elif string == 'processing':
            self._state = string
        elif string == 'resolved':
            self._state = None

    def process(self) -> 'bool|Action':
        '''state -> processing, return true'''
        self.state = 'processing'
        return True
'''EffectBlocks End'''

class Card(GameComponent):
    def __init__(self, owner:'HalfBoard', name='default card', color:Literal['R', 'Y', 'B']|None=None, 
                 speed:int|None=None, discription:str|None=None, image:str|None=None, *effects):
        self.owner = owner
        self._name = name
        self._color = color
        self._speed: int|None = speed
        self._power: int|None = None
        self._discription = discription
        self._image = image

        self._effects: list[Effect] = []
        if effects != ():
            for effect in effects:
                self._effects.append(effect)
        
        self.on_face = False
        self._active: Literal['active', 'inactive']|None = None
        self._location: Pack|None = None

    @property
    def name(self) -> str|None:
        return self.name_attr(self._name)
    
    @property
    def color(self) -> Literal['R', 'Y', 'B']|None:
        return self.name_attr(self._color)
    
    @property
    def discription(self) -> str|None:
        return self.name_attr(self._discription)
    
    @property
    def image(self) -> str|None:
        return self._image if self.on_face else None
    
    @property
    def speed(self) -> int|None:
        return self.full_attr(self._speed)
    
    @property
    def power(self) -> int|None:
        return self.full_attr(self._power)
    
    @power.setter
    def power(self, new_power:int|None):
        self._power = new_power
    
    @property
    def effects(self) -> list['Effect']:
        result = self.full_attr(self._effects)
        return result if result else []
    
    @effects.setter
    def effects(self, value: list['Effect']):
        self._effects = value
    
    @property
    def location(self):
        return self._location
    
    @location.setter
    def location(self, new_location):
        if self._location != new_location:
            if self.location:
                print(f'location changed from {self.location} to {new_location}.')
                if isinstance(self.location, Deck):
                    self.on_face = True
                self.location.remove(self)
        if new_location:
            self._location = new_location
            if not isinstance(self.location, Zone):
                self._active = None
        else:
            print(f'{self} moved to {new_location}. Delete self.')
            del self

    @property
    def active(self):
        if isinstance(self.location, Zone):
            if not self._active:
                self._active = 'active'
            return self._active
        else:
            self._active = None
            return self._active

    @active.setter
    def active(self, state:Literal['active', 'inactive']):
        self._active = state

    def on_top(self):
        if isinstance(self.location, Zone) or isinstance(self.location, Deck) or isinstance(self.location, Graveyard):
            return True if self.location.on_top() == self else False
        else:
            # Hand doesn't have depth concept
            return False

    def reveal_type(self):
        if not self.on_face:
            return None
        else:
            if isinstance(self.location, Zone):
                if self.on_top():
                    return 'full'
                else:
                    return 'name'
            elif isinstance(self.location, Hand):
                return 'hand'
            elif isinstance(self.location, Graveyard):
                if self.on_top():
                    return 'full'
                else:
                    return None
            else:
                raise Exception('Cannot define if card is revealed!')

    def name_attr(self, _value):
        if self.reveal_type() in ['full', 'name']:
            return _value
        # 미완
        elif self.reveal_type() == 'hand':
            return _value
        else:
            return None
        
    def full_attr(self, _value):
        if self.reveal_type() == 'full':
            return _value
        elif self.reveal_type() == 'hand':
            return _value
        else:
            return None

'''Card Types'''
class Creature(Card):
    class _CreatureAttackEffect(Effect):
        _name = 'AttackEffect'
        bind_to: 'Creature'
        choice: 'Creature._CreatureAttackEffect._AttackButtonChoice|SelectPlaceChoice'

        class _AttackButtonChoice(ButtonChoice, GivePlaceEvent):
            targets: list['Pack'] = []
            name = 'PressAttackButton'
            def match(self, key:'GameComponent|str|Choice|None', index:int|None):
                if key == self.key:
                    for zone in self.effect.board.opponent(self.effect.bind_to.halfboard).zones:
                        card = zone.on_top()
                        if card and card.power:
                            self.targets.append(zone)
                    if not self.targets:
                        self.targets = [self.effect.board.opponent(self.effect.bind_to.halfboard).hand]
                    return True
                else:
                    return False

        def _execute(self, in_event: 'Choice|Action|None') -> 'Choice|Action|None':
            if self.chosen(in_event):
                if self.choice.identifier == 0:
                    assert isinstance(self.choice, self._AttackButtonChoice)
                    return SelectPlaceChoice(self, self.choice.targets, self.choice.image, name='AttackTargetChoice', identifier=1)
                elif self.choice.identifier == 1:
                    assert isinstance(self.choice, SelectPlaceChoice)
                    if isinstance(self.choice.place, Hand):
                        print('Direct Attack!')
                        return DirectAttack(self, self.bind_to, self.choice.place.halfboard)
                    elif not isinstance(self.choice.place, Zone):
                        print(f'Attack should target Zone but targetted {self.choice.place}!')
                        return None
                    else:
                        return Attack(self, self.bind_to, self.choice.place)
            else:
                if (self.bind_to.is_for_current_player() and
                        self.bind_to.location == self.board.current_player.main_zone and
                        self.bind_to.active == 'active' and
                        self.bind_to.power):
                    if self.choice and self.choice.identifier == 0:
                        return self.choice
                    else:
                        return self._AttackButtonChoice(self, image='./images/choice_attack.png', identifier=0)
                else:
                    return None
    
    def __init__(self, owner:'HalfBoard', name='default creature', color=None,
                 power=1, speed=None, discription=None, image=None, *effects):
        super().__init__(owner, name, color, speed, discription, image, *effects)
        self.power = power
        self._effects.append(self._CreatureAttackEffect(self))

class Spell(Card):
    def __init__(self, owner:'HalfBoard', name='default spell', color=None,
                 speed=1, discription=None, image=None):
        super().__init__(owner, name, color, speed, discription, image)

class Artifact(Card):
    def __init__(self, owner:'HalfBoard', name='default artifact', color=None,
                 speed=None, discription=None, image=None):
        super().__init__(owner, name, color, speed, discription, image)
'''Card Types End'''

class NoCardError(Exception):
    pass
class NoPlaceError(Exception):
    pass

'''Actions'''
class Move(Action):
    card: Card
    place: 'Pack'
    def __init__(self, effect: Effect | None, card:Card, place:'Pack', name:str='Move') -> None:
        super().__init__(effect, name)
        self.card = card
        self.place = place

    def process(self):
        if not super().process():
            return False
        if not hasattr(self, 'card') or not self.card:
            raise NoCardError
        elif not hasattr(self, 'place') or not self.place:
            raise NoPlaceError
        else:
            self.place.append(self.card)
            return True

class Discard(Move):
    place:'Graveyard'
    def __init__(self, effect: Effect | None, card:Card, place:'Graveyard|None'=None, name:str='Discard'):
        if not place:
            if effect:
                place = effect.bind_to.halfboard.graveyard
            else:
                raise Exception('Effect or place is needed in Discard!')
        super().__init__(effect, card, place, name)
    
    def process(self):
        if hasattr(self, 'place') and not isinstance(self.place, Graveyard):
            raise Exception('Must discard in Graveyard!')
        else:
            return super().process()

class Attack(Action):
    def __new__(cls, effect: Effect|None, card:Card, place:'Zone', name:str='Attack'):
        if not card.power:
            print(f'Attacking card {card} should have power! Attack Init Failed.')
            return None
        else:
            return super().__new__(cls)

    def __init__(self, effect: Effect|None, card:Card, place:'Zone', name:str='Attack') -> None:
        super().__init__(effect, name)
        self.card = card    # Attacker
        self.place = place  # Attacking Place
        self.finished: bool = False

    def process(self):
        if self.finished:
            self.state = 'processing'
            self.card.active = 'inactive'
            return True

        if not super().process():
            return False
        if not hasattr(self, 'card') or not self.card:
            raise NoCardError
        elif not hasattr(self, 'place') or not self.place:
            raise NoPlaceError
        if not isinstance(self.place, Zone):
            print('You must attack zone!')
            return False
        if self.card.power is None:
            print(f'Attacking card {self.card} should have power! Attack process failed.')
            return False
        
        target = self.place.on_top()
        if not target or target.power is None:
            print(f"{target} has no power -> Cannot Attack! Act kept.")
            return False
        else:
            atk_power_tot: int = self.calculate_power(self.card)
            def_power_tot: int = self.calculate_power(target)

            if def_power_tot < atk_power_tot:
                self.finished = True
                self.state = 'pending'
                return self.place.get_collapse(effect=None) # Attack Collapse by Core Rule. Cannot be nulified by effect changes.
            else:
                print('Stronger Target -> No Damage.')
                self.card.active = 'inactive'
                return False

    def calculate_power(self, card:Card) -> int:
        assert card.power is not None
        total_power: int = card.power
        if isinstance(card.location, MainZone):
            for zone in card.location.halfboard.row.subzones:
                p = zone.get_power()
                if p:
                    total_power += p
        elif isinstance(card.location, SubZone):
            p = card.location.halfboard.main_zone.get_power()
            if p:
                total_power += p
        else:
            raise Exception('card location is not zone!')
        return total_power

class DirectAttack(Attack):
    def __new__(cls, effect: Effect|None, card:Card, halfboard:'HalfBoard', name:str='Attack'):
        if not card.power:
            print(f'Attacking card {card} should have power! Attack Init Failed.')
            return None
        else:
            return super(Attack, cls).__new__(cls)

    def __init__(self, effect:Effect|None, card:Card, halfboard:'HalfBoard', name:str='DirectAttack') -> None:
        super(Attack, self).__init__(effect, name)
        self.card = card
        self.target = halfboard

    def process(self):
        if not super(Attack, self).process():
            return False
        if not hasattr(self, 'card') or not self.card:
            raise NoCardError
        if self.card.power is None:
            print(f'Attacking card {self.card} should have power! Attack process failed.')
            return False
        
        atk_power_tot: int = self.calculate_power(self.card)
        if atk_power_tot > 0:
            self.finished = True
            self.state = 'pending'
            return self.target.get_loseaction(self.effect)
        else:
            print('total power is less or equal than 0. Direct Attack failed.')
            return False

class Activate(Action):
    pass
'''Actions End'''

'''HalfBoard Components'''
class Pack(GameComponent):            
    class _CardIntoPackChoice(GiveCardEvent, GivePlaceEvent, Choice):
        _key: 'Pack|None' = None
        name = 'CardIntoPackChoice'

        def match(self, key:GameComponent|None, index:int|None):
            if self.effect.board.holding_from != self.key and self.key == key and \
                isinstance(self.effect.board.holding, Card) and isinstance(self.effect.board.holding_from, Pack):
                print(f'Dragged into {self.effect.bind_to}!')
                self.card = self.effect.board.holding
                self.place = self.effect.board.holding_from
                return True
            else:
                return False

    def __init__(self, halfboard:'HalfBoard', name:str|None=None):
        self._cards: list[Card] = []
        self._halfboard = halfboard
        self.effects: list[Effect] = []
        self.name = name if name else 'Dummy Pack'

    def __repr__(self) -> str:
        return f"<{self.name} at {hex(id(self))}>"

    @property
    def length(self):
        return len(self._cards)

    def append(self, card:Card):
        self._cards.append(card)
        card.location = self

    def remove(self, card:Card):
        if card in self._cards:
            self._cards.remove(card)
        else:
            raise Exception('No such Card in this Pack!')

    def pop(self, index=None):
        if self.is_empty():
            raise Exception("Tryed to pop an Empty Pack!")
        else:
            return self._cards[index] if index else self._cards[-1]

    def is_empty(self, num=None):
        if num:
            return True if self.length >= num else False
        else:
            return True if self.length == 0 else False

    def get_card_into_pack_choice(self, effect:Effect, chooser:Literal['self', 'opponent']='self'):
        return self._CardIntoPackChoice(effect, self, chooser)

class Deck(Pack):
    class _DrawAction(Action):
        '''단독으로 쓰지 말 것'''
        deck: 'Deck'
        def __init__(self, effect:'Effect|None', num:int, deck:'Deck', name:str='Draw'):
            super().__init__(effect, name)
            self.deck = deck
            self.num = num

        def process(self):
            super().process()
            for _ in range(self.num):
                card = self.deck.pop()
                card._active = None
                self.deck.halfboard.hand.append(card)
            return True
        
    class _TurnDrawAction(_DrawAction):
        def __init__(self, effect: Effect, deck: 'Deck'):
            super().__init__(effect, 1, deck, 'TurnDraw')

        def process(self):
            if super().process():
                self.deck.turndrawed = True
                return True
            else:
                return False
            
    class _TurnDrawEffect(Effect):                
        def __init__(self, deck: 'Deck'):
            super().__init__(deck, 'TurnDrawEffect')
            self.bind_to = deck

        def _execute(self, in_event: Choice | Action | None):
            if self.chosen(in_event):
                return self.bind_to.turndraw(self)
            elif self.bind_to.is_for_current_player() and not self.bind_to.turndrawed:
                if self.bind_to.is_empty():
                    return self.bind_to.halfboard.get_loseaction(self)
                else:
                    return Choice(self, key=self.bind_to, name='ClickDeck')
            
    def __init__(self, halfboard:'HalfBoard'):
        super().__init__(halfboard, f"{halfboard.name}'s deck")
        self.turndraw_effect = self._TurnDrawEffect(self)
        self.turndrawed = False
        self.effects.append(self.turndraw_effect)

    def on_top(self):
        if self.length > 0:
            return self._cards[0]
        else:
            return None
        
    def shuffle(self):
        '''나중에 셔플 유발 효과가 생기면 통째로 Action으로 변경'''
        shuffle(self._cards)

    def draw(self, effect:Effect|None=None, num:int=1):
        return self._DrawAction(effect, num, self)
    
    def turndraw(self, effect:'Deck._TurnDrawEffect'):
        return self._TurnDrawAction(effect, self)

class Graveyard(Pack):
    def __init__(self, halfboard:'HalfBoard'):
        super().__init__(halfboard, f"{halfboard.name}'s Graveyard")

    def on_top(self):
        if not self.is_empty():
            return self._cards[-1]
        else:
            return None

class Hand(Pack):
    def __init__(self, halfboard:'HalfBoard'):
        super().__init__(halfboard, f"{halfboard.name}'s hand")

class Zone(Pack):
    name='Error: just a Zone'
    class Let(Move):
        effect: Effect
        def __init__(self, effect: Effect, card:Card, place:'Zone'):
            super().__init__(effect, card, place, 'Let')

        def process(self):
            super().process()
            if not self.card:
                raise NoCardError
            elif not self.place:
                raise NoPlaceError
            
            if not isinstance(self.place, Zone):
                raise Exception('Let should be on Zone!')
            self.card._active = 'inactive'
            self.effect.board.drop_holding()
            self.place.has_been_let = True
            return True
        
    class Collapse(Action):
        def __init__(self, effect: Effect | None, place:'Zone') -> None:
            super().__init__(effect, 'Collapse')
            self.place = place

        def process(self):
            if not self.place:
                raise NoPlaceError
            if not isinstance(self.place, Zone):
                raise Exception('Collapse must be on Zone!')
            
            super().process()
            if card := self.place.on_top():
                self.state = 'pending'
                discard_action = Discard(self.effect, card)
                return discard_action
            else:
                self.state = 'processing'
                return True

    def __init__(self, halfboard:'HalfBoard', name:str|None=None):
        super().__init__(halfboard, name if name else self.name)
        self.has_been_let = False

    def on_top(self):
        if not self.is_empty():
            return self._cards[-1]
        else:
            return None

    def is_collapsing(self, effect:Effect|None=None):
        '''"자기 턴이고" "그 턴이 끝났고" "Let 된 적 없고" "예약되지 않았으면"'''
        return self.is_for_current_player() and self.board.turn_end and not self.has_been_let

    def get_collapse(self, effect:Effect|None=None):
        return self.Collapse(effect, self)

    def get_power(self):
        '''return top card's power.'''
        topcard = self.on_top()
        if topcard and topcard.power is not None:
            return topcard.power
        else:
            return None

class MainZone(Zone):
    class MainZoneCollapse(Zone.Collapse):
        def process(self):
            super().process()
            return self.place.halfboard.get_loseaction(self.effect if self.effect else None)
        
    class _LetEffect(Effect):
        bind_to: 'MainZone'
        choice: GiveCardEvent
        _name='LetEffect'
        class _MainZoneLetAction(Zone.Let):
            '''Let 후 turn_end 활성화'''
            def process(self):
                result = super().process()
                self.effect.board.turn_end = True
                return result

        def _execute(self, in_event: Choice | Action | None):
            if self.chosen(in_event):
                if self.choice.card.active != 'inactive':
                    action = self._MainZoneLetAction(self, self.choice.card, self.bind_to)
                else:
                    action = None
                return action
                
            elif self.bind_to.is_for_current_player() and not self.board.turn_end:
                return self.bind_to.get_card_into_pack_choice(self)
                
    class _MainZoneCollapseEffect(Effect):
        bind_to: 'MainZone'
        _name='CollapseEffect'
        def execute(self, in_event: Choice | Action | None):
            if self.bind_to.is_collapsing(self):
                return self.bind_to.MainZoneCollapse(self, self.bind_to)

    def __init__(self, halfboard:'HalfBoard'):
        super().__init__(halfboard, f"{halfboard.name}'s Main Zone")

        self.let = self._LetEffect(self)
        self.collapse = self._MainZoneCollapseEffect(self)
        self.effects.append(self.let)
        self.effects.append(self.collapse)

    def is_collapsing(self, effect: Effect | None = None):
        return self.is_for_current_player() and self.board.turn_end and not self.has_been_let

class SubZone(Zone):
    index: int

    class Collapse(Zone.Collapse):
        place: 'SubZone'
        def process(self):
            result = super().process()
            if result == True:
                self.place.row.remove(self.place)
                del self.place
            return result
        
    class _LetEffect(Effect):
        bind_to: 'SubZone'
        choice: GiveCardEvent

        class _SubZoneLetAction(Zone.Let):
            effect: 'SubZone._LetEffect'
            def generate(self, card:Card|None):
                if card:
                    self.card = card
                if not hasattr(self, 'card') or self.card == None:
                    if self.effect.bind_to.init_card:
                        self.card = self.effect.bind_to.init_card
                    else:
                        raise Exception('No card to Let!')
            
            def process(self):
                result = super().process()
                # If was first Let, finish initialization.
                if self.effect.bind_to.init_card:
                    self.effect.bind_to.init_card = None
                return result
        
        def __init__(self, bind_to:'SubZone'):
            super().__init__(bind_to)
            self.bind_to = bind_to
        
        def _execute(self, in_event: Choice | Action | None):
            if self.chosen(in_event):
                if self.choice.card.active != 'inactive':
                    card = self.choice.card
                else:
                    return None
            elif self.bind_to.is_for_current_player():
                if self.bind_to.init_card and not in_event:
                    card = self.bind_to.init_card
                else:
                    return self.bind_to._CardIntoPackChoice(self, self.bind_to)
            else:
                return None
            return self._SubZoneLetAction(self, card, place=self.bind_to)

    class _SubZoneCollapseEffect(Effect):
        bind_to: 'SubZone'

        def execute(self, in_event: Choice | Action | None):
            if (self.bind_to.is_empty() and not self.bind_to.init_card) or\
                self.bind_to.is_collapsing(self):
                return self.bind_to.Collapse(self, self.bind_to)

    def __init__(self, halfboard):
        super().__init__(halfboard)
        self.init_card: Card|None = None
        self.let = self._LetEffect(self)
        self.CollapseEffect = self._SubZoneCollapseEffect(self)
        self.effects.append(self.let)
        self.effects.append(self.CollapseEffect)

    @property
    def row(self):
        if self in self.halfboard.row.subzones:
            return self.halfboard.row
        else:
            raise Exception('Lonely SubZone!')

class Row(GameComponent):
    class Deploy(Action):
        def __init__(self, effect: Effect | None, card:Card, row:'Row', num:int) -> None:
            super().__init__(effect, 'Deploy')
            self.card = card
            self.row = row
            self.new_index = num

        def process(self):
            super().process()
            new_subzone = self.row.create_subzone(self.new_index)
            new_subzone.init_card = self.card
            self.state = 'resolved'
            return True

    class _DeployEffect(Effect):
        bind_to: 'Row'
        choice: 'Row._DeployEffect._TempZoneChoice'
        _name='DeployEffect'

        class _TempZoneChoice(Choice, GiveCardEvent):
            subzone_index: int
            name='DropOnTempZone'
            def __init__(self, effect:Effect):
                super().__init__(effect, key='temp zone')

            def match(self, key:GameComponent|str, index:int|None):
                if isinstance(self.effect.board.holding, Card) and self.key == key and \
                   self.effect.bind_to.is_for_current_player():
                    if index:
                        self.subzone_index = index - 1
                    else:
                        raise Exception('No index while Deploying!')
                    self.card = self.effect.board.holding
                    return True
                else:
                    return False

        def __init__(self, bind_to:'Row'):
            super().__init__(bind_to)

        def _execute(self, in_event: Choice | Action | None):
            if self.chosen(in_event):
                if self.choice.card.active != 'inactive':
                    action = self.bind_to.Deploy(self, self.choice.card, self.bind_to, self.choice.subzone_index)
                else:
                    action = None
                return action
            elif self.bind_to.is_for_current_player() and len(self.bind_to.subzones) < 3:
                return self._TempZoneChoice(self)


    def __init__(self, halfboard:'HalfBoard'):
        self._halfboard = halfboard
        self.name = f"{self.halfboard.name}'s Row"
        self.subzones: list[SubZone] = []
        self.Deploy = type('Deploy', (Row.Deploy,), {'row': self})
        self.DeployEffect = self._DeployEffect(self)
        self.effects: list[Effect] = [self.DeployEffect]

    def rename(self):
        for subzone in self.subzones:
            subzone.index = self.subzones.index(subzone)
            subzone.name = f"{self.halfboard.name}'s Sub Zone {subzone.index}"

    def create_subzone(self, index):
        new_subzone = SubZone(self.halfboard)
        self.subzones.insert(index, new_subzone)
        self.rename()
        return new_subzone

    def remove(self, subzone:SubZone):
        self.subzones.remove(subzone)
        self.rename()
'''HalfBoard Components End'''

class HalfBoard(GameComponent):
    _board: 'Board'
    cardlist: list[type[Card]] = []

    class _LoseAction(Action):
        def __init__(self, effect: Effect|None, loser:'HalfBoard'):
            super().__init__(effect, 'LoseAction')
            self.loser = loser

        def process(self):
            super().process()
            print(f'Due to: {self.effect}')
            self.loser.board.loser = self.loser
            raise Board.End

    def __init__(self, player_name:str):
        self.name = player_name
        self.deck = Deck(self)
        self.graveyard = Graveyard(self)
        self.main_zone = MainZone(self)
        self.row = Row(self)
        self.hand = Hand(self)
        self.effects: list[Effect] = []
        self.available_choices: list[Choice] = []

    @property
    def zones(self):
        return [self.main_zone] + self.row.subzones
    
    @property
    def board(self):
        if hasattr(self, '_board'):
            return self._board
        else:
            raise AttributeError('No Board for HalfBoard - Maybe not Initialized.')

    def get_loseaction(self, effect:Effect|None):
        return self._LoseAction(effect, self)

class Board(GameComponent):
    class End(Exception):
        pass

    class CoreEffect(Effect):
        class CoreRestriction(Restriction):
            '''"EffectBlock의 Effect가 유효할 것."'''
            def verify(self, event:Event):
                if event.effect:
                    if event.effect.is_valid():
                        return True
                    else:
                        return False
                else:
                    return True
                
        def __init__(self, bind_to: 'Board'):
            super().__init__(bind_to)
            self.effectblocks = [
                self.CoreRestriction(self, 'Core Rule')
                ]
            
        def is_valid(self):
            '''Core rule은 언제나 valid.'''
            return True

    class InitialSetting(Effect):
        bind_to: 'Board'
        yieldactions: list[Action]|None = None
        def _execute(self, in_event):
            if self.yieldactions == []:
                self.yieldactions = None
                return None
            elif self.yieldactions:
                pass
            else:
                self.yieldactions = []
                for player in self.bind_to.players:
                    self.yieldactions.append(player.deck.draw(self, 5))
            return self.yieldactions.pop(0)

    def __init__(self, player1:HalfBoard, player2:HalfBoard):
        self.name = 'Board'
        self.effects = []
        self.player1 = player1
        self.player2 = player2
        self.players = [player1, player2]
        self.loser = False
        self.current_player: HalfBoard = player1
        self._turn = 0
        self.turn_end = False
        self.action_stack: list[Action] = []
        self.restrictions: list[Restriction] = []

        for player in self.players:
            player._board = self

        self.holding: GameComponent|Choice|str|None = None
        self.holding_from = None
        self.gamecomponents: list[Board|HalfBoard|Row|Pack|Card] = []
        self.keys_for_choices: dict[GameComponent|Choice|str, Choice] = {}

    @property
    def turn(self):
        return self._turn
    
    @turn.setter
    def turn(self, value:int):
        if value > self._turn:
            self.turn_end = False
        self._turn = value

    def opponent(self, player:HalfBoard|None=None) -> HalfBoard:
        if player == self.player1:
            return self.player2
        elif player == self.player2:
            return self.player1
        elif player == None:
            return self.opponent(self.current_player)
        else:
            raise ValueError(f'player was {player}: Could not find its opponent.')

    def refresh_gamecomponents(self):
        self.gamecomponents = [self]
        for player in self.players:
            self.gamecomponents.append(player)
            self.gamecomponents.append(player.deck)
            self.gamecomponents.append(player.hand)
            self.gamecomponents.append(player.graveyard)
            self.gamecomponents.append(player.row)
            gy_top_card = player.graveyard.on_top()
            if gy_top_card:
                self.gamecomponents.append(gy_top_card)
            for zone in player.zones:
                self.gamecomponents.append(zone)
                for card in zone._cards:
                    self.gamecomponents.append(card)
        return self.gamecomponents

    def get_processing_order(self):
        order: list[Card|Pack|Board|Row|HalfBoard|None] = []
        order.append(self)
        for player in [self.opponent(), self.current_player]:
            order.append(player)
            order.append(player.main_zone)
            order.append(player.graveyard)
            order.append(player.row)
            for zone in player.row.subzones:
                order.append(zone)
            order.append(player.deck)
            order.append(player.hand)

            if not player.main_zone.is_empty():
                order.append(player.main_zone.on_top())
            if not player.graveyard.is_empty():
                order.append(player.graveyard.on_top())
            for zone in player.row.subzones:
                order.append(zone.on_top())
        return order

    def get_keys_for_choices(self):
        self.keys_for_choices = {}
        for choice in self.current_player.available_choices:
            if isinstance(choice.key, list):
                for key in choice.key:
                    self.keys_for_choices[key] = choice
            elif choice.key:
                self.keys_for_choices[choice.key] = choice

    def initial_setting(self):
        '''시작 시 5장 뽑기. 여기서부터는 효과 처리가 필요하다.'''
        a = self.InitialSetting(self)
        action = a.execute(None)
        while action:
            assert isinstance(action, Action)
            action.process()
            action = a.execute(None)

    def interpret(self, typ:Literal['click', 'drop'], keys:list[GameComponent|Choice|str], index:int|None=None):
        key = None
        def key_searcher(keys, typ:type, sort:Literal['first', 'last']='first'):
            instances = [key for key in keys if isinstance(key, typ)]
            if instances:
                if sort == 'first':
                    return instances[0]
                elif sort == 'last':
                    return instances[-1]
                else:
                    raise Exception("sort isn't 'first' or 'last'!")
            else:
                return None
        
        if typ == 'click':
            for keytype in [Choice, str, Deck, Graveyard, Zone, Card, Row, HalfBoard, Board]:
                if keytype == Card:
                    if key := key_searcher(keys, keytype, 'last'):
                        break
                else:
                    if key := key_searcher(keys, keytype):
                        break
            
            if isinstance(key, str):
                self.holding = key
                self.holding_from = None
                print(f'you clicked {key}.')
            else:
                if isinstance(key, Choice):
                    self.holding = key
                    self.holding_from = key.effect.bind_to
                elif isinstance(key, Card):
                    self.holding = key
                    self.holding_from = self.holding.location
                elif isinstance(key, Zone) or isinstance(key, Graveyard):
                    if not key.is_empty():
                        self.holding_from = key
                        self.holding = self.holding_from.on_top()
                elif isinstance(key, Deck):
                    self.holding_from = key
                    self.holding = key
                print(f'you are holding {self.holding} from {self.holding_from}.')
            return True
        
        elif typ == 'drop':
            if 'endbutton' in keys and not self.turn%2:
                return 'endbutton'
            for key in keys:
                if key in self.keys_for_choices:
                    if self.keys_for_choices[key].match(key, index):
                        return self.keys_for_choices[key]

        else:
            raise Exception('Not click nor drop!')
        
        return False

    def drop_holding(self):
        print(f'you dropped {self.holding}.')
        self.holding = None
        self.holding_from = None

    def verify_restriction(self, event:Event):
        for restriction in self.restrictions:
            if restriction.effect and restriction.effect.is_valid():
                if not restriction.verify(event):
                    print('restriction met!')
                    return False
            else:
                self.restrictions.remove(restriction)
        return True

    def add_action(self, action:Action, chain:bool=False):
        # 여기서 action 추가 순서 정함 (체인인지, 유발인지지)
        action.state = 'pending'
        if chain:
            print(f'Action {action} chained to stack.')
            self.action_stack.insert(0, action)
        else:
            print(f'Action {action} appended to stack.')
            self.action_stack.append(action)

    def search_effect(self, in_event:Action|None=None):
        # Search Mode: In action or Idle.
        for gamecomponent in self.refresh_gamecomponents():
            for effect in gamecomponent.effects:
                event = effect.execute(in_event)
                if isinstance(event, Action):
                    self.add_action(event)
                elif isinstance(event, Choice):
                    event.chooser.available_choices.append(event)

    def play(self):
        for player in self.players:
            if len(player.cardlist) == 0:
                for i in range(10):
                    new_card = Card(player, str(f'{player}'+f'{-i}'))
                    player.deck.append(new_card)
            else:
                for cardclass in player.cardlist:
                    player.deck.append(cardclass(player))
            player.deck.shuffle()

        self.initial_setting()
        # Debug
        self.player2.main_zone.append(Card(self.player2, 'main card'))

        while not self.loser:
            # Catch losing condition
            try:
                # Turn Init
                self.turn_end = False
                self.turn += 1
                self.current_player = self.player1 if self.turn%2 else self.player2
                print('start turn')
                self.action_stack = []
                for player in self.players:
                    player.available_choices = []
                    for zone in player.zones:
                        zone.has_been_let = False
                        if player == self.current_player:
                            for card in zone._cards:
                                card._active = None
                    player.deck.turndrawed = False

                # Main Phase
                while not self.turn_end:
                    running = True
                    # Not Idle state.
                    while running:
                        # Action stack search
                        while len(self.action_stack) > 0:
                            current_action = self.action_stack[0]
                            print(f'Current Action:{current_action}. ', end="")
                            # Invalid Action
                            if not current_action.is_valid():
                                print('But From Invalid Effect. Erase.')
                            # Valid Action
                            else:
                                print('Start searching chain.')
                                self.search_effect(current_action)  # Trigger Mode
                                # If Action changed, run another search. pass.
                                if current_action != self.action_stack[0]:
                                    print(f'Chain {self.action_stack[0]} found. Run another Search.')
                                # Action was kept; No Chain.
                                else:
                                    print('Action kept,', end=' ')
                                    # Doesn't pass restriction -> Nothing happens.
                                    if not self.verify_restriction(current_action):
                                        print("But Action couldn't pass restriction.")
                                    # Passes restriction.
                                    else:
                                        print('Processing...')
                                        result = current_action.process()
                                        # current_ action has other actions to be handled first.
                                        if isinstance(result, Action):
                                            print(f'Action {current_action} has prior action {result}.')
                                            self.add_action(result, True)
                                            continue
                                        # else. current_action is normally done.
                                    
                            # action removal.
                            print(f"{current_action} is removed.")
                            current_action.state = 'resolved'
                            self.action_stack.remove(current_action)
                           
                        # There are no action. Run idle search.
                        print('Action stack emptied. Try Idle Search.')
                        self.drop_holding()     # Chain is over; No holding card.
                        # Initialize choices.
                        self.current_player.available_choices = []
                        self.search_effect()    # Idle Mode
                        # Escape if there's still no action.
                        if len(self.action_stack) == 0:
                            running = False
                    # running end

                    # Check turn end here. If changed, break.
                    if self.turn_end:
                        continue

                    # Else, Player choose what to do.
                    print('No Idle Action. Can choose now.')
                    chossing: bool = True
                    self.get_keys_for_choices()
                    while chossing:
                        print(f'Choices: {self.current_player.available_choices}')
                        args: tuple[Literal['click', 'drop', 'rightclick'], list, int|None] = yield
                        if type(args) == tuple:
                            print('got tuple yield')
                            typ, keys, index = args
                            if (typ == 'click' or typ == 'drop') and isinstance(keys, list):
                                choice = self.interpret(typ, keys, index)
                                # If not valid choice, reset the holding card.
                                if choice == False:
                                    self.drop_holding()
                                # If choice is valid, break. Give the output action to the stack.
                                elif isinstance(choice, Choice):
                                    print(f'your choice is {choice}.')
                                    result = choice.effect.execute(choice)
                                    if isinstance(result, Choice):
                                        print(f'lead to new choice {result}...')
                                        self.current_player.available_choices = [result]
                                        self.get_keys_for_choices()
                                        if typ == 'drop':
                                            self.drop_holding()
                                    elif isinstance(result, Action):
                                        self.add_action(result)
                                        chossing = False
                                    else:
                                        print('Your choice made no following event! Get Idle choices.')
                                        chossing = False
                                # Debug Endbutton.
                                elif choice == 'endbutton':
                                    self.turn_end = True
                                    chossing = False
                            # Cancel
                            elif typ == 'rightclick':
                                chossing = False
                                self.drop_holding()
                        else:
                            print('yield is not a tuple!')

                    # Go back to action stack search

                # When self.turn_end is True, loop breaks.
                print('end turn')

            # Losing Condition
            except self.End:
                print('Game Finished!')
                if not self.loser:
                    self.loser = self.current_player
                    print('game ended, but loser is not clear. '
                          f'the opponent {self.opponent(self.loser)} survives.')
                yield 'end!'    # After this, No more play() call.
            # try-except end

        # After self.loser
        raise Exception('UI calls finished game!')

# Usage:
#   player1 = HalfBoard('Player 1')
#   player2 = HalfBoard('Player 2')
#   game = Board(player1, player2)
#   gameplay = game.play()
#   gameplay.send(tuple[Literal['click', 'drop'], list, int|None])