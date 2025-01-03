from typing import Callable, Literal, Union, List, Any, Generator
from random import shuffle
LOSE = 'lose'

class GameComponent:
    _halfboard: 'HalfBoard'
    effects: list['Effect']

    def __init__(self, halfboard:'HalfBoard'):
        raise Exception("Called Abstract Class!")

    @property
    def halfboard(self):
        if isinstance(self, HalfBoard):
            return self
        elif isinstance(self, Card):
            return self.owner
        else:
            return self._halfboard
    
    @halfboard.setter
    def halfboard(self, hb:'HalfBoard'):
        self._halfboard = hb

    def is_for_current_player(self):
        if self.halfboard.board.current_player == self.halfboard:
            return True
        else:
            return False
    
    # For Packs only
    def clicked(self):
        '''Checks if clicked and droped on same place'''
        if self.halfboard.board.holding == self:
            return True
        else:
            return False

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

    def on_top(self):
        if isinstance(self.location, Zone) or isinstance(self.location, Deck):
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
    def __init__(self, owner:'HalfBoard', name='default creature', color=None,
                 power=1, speed=None, discription=None, image=None, *effects):
        super().__init__(owner, name, color, speed, discription, image, *effects)
        self.power = power

class Spell(Card):
    def __init__(self, owner:'HalfBoard', name='default spell', color=None,
                 speed=1, discription=None, image=None):
        super().__init__(owner, name, color, speed, discription, image)

class Artifact(Card):
    def __init__(self, owner:'HalfBoard', name='default artifact', color=None,
                 speed=None, discription=None, image=None):
        super().__init__(owner, name, color, speed, discription, image)
'''Card Types End'''

class Effect:
    '''bind_to, effectblocks, board, is_valid'''
    def __init__(self, bind_to:GameComponent):
        self.bind_to = bind_to
        self.effectblocks: list['EffectBlock'] = []
        '''How to Use: (EffectBlock, next index if True, next index if False)'''

    @property
    def board(self):
        if not self.bind_to:
            raise Exception("Tried to load Board from free Effect!")
        elif isinstance(self.bind_to, Board):
            return self.bind_to
        else:
            return self.bind_to.halfboard.board
    
    def is_valid(self):
        if self.bind_to:
            if isinstance(self.bind_to, Card):
                if self.bind_to.reveal_type():
                    return True
                else:
                    return False
            elif isinstance(self.bind_to, SubZone):
                try:
                    return bool(self.bind_to.row)
                except Exception:
                    return False
            else:
                return True
        else:
            print(f'Effect {self} has no bind_to! Delete.')
            del self
            return False
        
    def is_reserved(self):
        for action in self.board.action_stack:
            if action.effect == self:
                print(f'{self} is not recursive effect. Ignore.')
                return True
        return False

class EffectBlock:
    def __init__(self, effect:Effect, *index:int|None):
        self.effect = effect
        self.next_indexes = index

    @property
    def index(self):
        # Single Action
        if not self.effect:
            return None
        # Action in Effect
        for i, eb in enumerate([eb for eb in self.effect.effectblocks]):
            if eb == self:
                return i
        # If there's no matching index:
        raise Exception('Effectblock not included in Effect!')
        
    def get_next_effblock(self, result:bool|int):
        if result == True:
            index = 0
        elif result == False:
            index = 1
        elif result:
            index = result
        else:
            return None
        if len(self.next_indexes) >= index + 1:
            next_index = self.next_indexes[index]
            if next_index:
                next_effblock = self.effect.effectblocks[next_index]
                return next_effblock
        elif index == 1:
            return None
        elif index == 0 and not isinstance(self, Condition):
            return None
        else:
            raise Exception(f'No instruction after {self}!')



    def add_parameter(self, param:dict[str, Any]|None):
        if param:
            for key in param:
                setattr(self, key, param[key])

    def give_parameter(self, param:dict|None):
        return param

'''EffectBlocks'''
class Condition(EffectBlock):
    def __init__(self, effect:Effect, *index:int|None, check:Callable[..., bool|int]|None=None):
        super().__init__(effect, *index)
        if check:
            self.check = check

    def check(self, in_action:'Action|bool') -> bool|int :
        if self.effect.is_valid():
            if isinstance(in_action, Action):
                self_checking = bool(in_action.effect == self.effect)
                if self_checking:
                    print(f'Self-checking {self} -> Ignore.')
                    return False
                else:
                    return True
            elif in_action:
                raise Exception("Action can't be just 'True'!")
            else:
                return True
        else:
            print(f'Effect is not valid! Condition {self} ignored.')
            return False

class _GetCardActiveCondition(Condition):
    '''{0: inactive, 1: active, 2: None}'''
    def __init__(self, effect: Effect, *index):
        super().__init__(effect, *index)
        self.card: Card|None = None

    def check(self, in_action: 'Action | bool') -> bool | int:
        if super().check(in_action) and self.card:
            if self.card.active == None:
                return 2
            elif self.card.active == 'active':
                return 1
            elif self.card.active == 'inactive':
                return 0
        return False

class Restriction(EffectBlock):
    def verify(self, eb:'EffectBlock') -> bool:
        return True

class Choice(EffectBlock):
    image: str|None = None
    def __init__(self, effect: Effect, *index, key:GameComponent|Literal['temp zone']|None=None,
                 has_button:bool=False, image:str|None=None):
        super().__init__(effect, *index)
        self.is_button: bool = False
        if key:
            self._key = key
        elif has_button:
            if isinstance(self.effect.bind_to, Card):
                self.is_button = True
                self.image = image
                self._key = self
            else:
                raise Exception('Button must be on Card!')
        else:
            self._key = self.effect.bind_to

    @property
    def key(self):
        if self.effect.is_valid():
            return self._key
        else:
            return None
        
    @key.setter
    def key(self, key:GameComponent):
        self._key = key

    def match(self, key:'GameComponent|str|Choice|None', index:int|None) -> bool:
        return True if self.key == key else False
    
    def clicked(self):
        return True if self.effect.board.holding == self else False

class Action(EffectBlock):
    state: Literal['pending', 'processing', 'paused', 'resolved']|None = None

    def generate(self, **kwargs):
        self.state = 'pending'

    def process(self) -> 'bool|Action':
        '''state -> resolved, return true'''
        self.state = 'processing'
        return True
    
'''EffectBlocks End'''

'''Actions'''
class Move(Action):
    def generate(self, card:Card, destination:'Pack'):
        self.card = card
        self.destination = destination

    def process(self):
        super().process()
        if not self.card:
            raise Exception('Move was called without card!')
        else:
            self.state = 'processing'
            self.destination.append(self.card)
            return True
    
class Discard(Move):
    destination: 'Graveyard'
    def generate(self, card: Card, destination:'Graveyard|None'=None):
        if not destination:
            self.destination = card.owner.graveyard
        elif not isinstance(destination, Graveyard):
            raise Exception('Discard must be to Graveyard!')
        super().generate(card, self.destination)

class Attack(Action):
    pass

class Activate(Action):
    pass
'''Actions End'''

'''GameComponents'''
class Pack(GameComponent):
    class _IsEmptyCondition(Condition):
        pack: 'Pack|None' = None
        def __init__(self, effect, *index, num=None):
            super().__init__(effect, *index)
            self.num = num

        def check(self, in_action):
            if not self.pack:
                raise AttributeError
            base_condition = super().check(in_action)
            if self.num:
                return self.pack.is_empty(self.num) and base_condition
            else:
                return self.pack.is_empty() and base_condition
            
    class _DragIntoPackChoice(Choice):
        _key: 'Pack|None' = None

        def __init__(self, effect:Effect, *index):
            if not self._key:
                raise AttributeError
            super().__init__(effect, *index, key=self._key)

        def match(self, key:GameComponent|None, index:int|None):
            if self.effect.board.holding_from != self.key and self.key == key:
                print(f'Dragged into {self.effect.bind_to}!')
                return True
            else:
                return False
            
        def give_parameter(self, param:dict):
            return {'card': self.effect.board.holding}

    def __init__(self, halfboard:'HalfBoard'):
        self._cards: list[Card] = []
        self.halfboard = halfboard
        self.effects: list[Effect] = []
        self._IsEmptyCondition = type('_IsEmptyCondition', (Pack._IsEmptyCondition,), {'pack': self})
        self._DragIntoPackChoice = type('_DragIntoPackChoice', (Pack._DragIntoPackChoice,), {'_key': self})

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

class Deck(Pack):
    class _DrawAction(Action):
        '''단독으로 쓰지 말 것'''
        deck: 'Deck|None'=None
        def __init__(self, effect:'Effect', *index, deck:Union['Deck', None]=None):
            super().__init__(effect, *index)
            if deck:
                self.deck = deck
            elif isinstance(self.deck, Deck):
                pass
            elif isinstance(self.effect.bind_to, Deck):
                self.deck = self.effect.bind_to
            else:
                raise Exception('No deck for DrawAction!')

        def generate(self, num:int=1):
            if not self.deck:
                raise AttributeError
            self.num = num

        def process(self):
            if not self.deck:
                raise AttributeError
            super().process()
            for _ in range(self.num):
                card = self.deck.pop()
                card._active = None
                self.deck.halfboard.hand.append(card)
            return True
        
    # _DrawAction 상속을 위해 밖으로 뺌뺌
    class _TurnDrawAction(_DrawAction):
        deck: 'Deck|None' = None
        def generate(self, num=1):
            self.num = num

        def process(self):
            if not self.deck:
                raise AttributeError
            if super().process():
                self.deck.turndrawed = True
                return True
            else:
                return False
            
    class _TurnDrawEffect(Effect):
        class _TurnDrawCondition(Condition):
            effect: 'Deck._TurnDrawEffect'
            def check(self, in_action):
                return super().check(in_action) and \
                       self.effect.bind_to.is_for_current_player() and \
                       bool(not self.effect.bind_to.turndrawed)
            
        class _TurnDrawChoice(Choice):
            def match(self, key:GameComponent, index:int|None):
                return super().match(key, index) and self.effect.bind_to.clicked()
                
        def __init__(self, deck: 'Deck'):
            super().__init__(deck)
            self.bind_to = deck
            self.effectblocks = [
                self._TurnDrawCondition(self, 1),
                self.bind_to._IsEmptyCondition(self, 4, 2),
                self._TurnDrawChoice(self, 3, None, key=deck),
                self.bind_to._TurnDrawAction(self),
                self.bind_to.halfboard.get_loseaction(self)
            ]

    def __init__(self, halfboard):
        super().__init__(halfboard)
        self._DrawAction = type('_DrawAction', (Deck._DrawAction,), {'deck': self})
        self._TurnDrawAction = type('_TurnDrawAction', (Deck._TurnDrawAction,), {'deck': self})
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

class Graveyard(Pack):
    def __init__(self, halfboard):
        super().__init__(halfboard)

    def on_top(self):
        if not self.is_empty():
            return self._cards[-1]
        else:
            return None

class Hand(Pack):
    def __init__(self, halfboard:'HalfBoard'):
        super().__init__(halfboard)
        self.name = f"{self.halfboard.name}'s hand"

class Zone(Pack):
    class Let(Move):
        destination: 'Zone'
        def __init__(self, effect: Effect, *index, destination:'Zone'):
            super().__init__(effect, *index)
            self.destination = destination

        def generate(self, card:Card):
            self.card = card

        def process(self):
            super().process()
            self.card._active = 'inactive'
            self.effect.board.drop_holding()
            self.destination.has_been_let = True
            self.state = 'resolved'
            return True
        
    class Collapse(Action):
        zone: 'Zone|None' = None
        def generate(self, zone: 'Zone|None'):
            if zone:
                self.zone = zone

        def process(self):
            if not self.zone:
                raise AttributeError
            super().process()
            if card := self.zone.on_top():
                self.state = 'paused'
                discardaction = Discard(self.effect)
                discardaction.generate(card)
                return discardaction
            else:
                self.state = 'processing'
                return True

    class _ZoneCollapseCondition(Condition):
        '''"자기 턴이고" "그 턴이 끝났고" "Let 된 적 없고" "예약되지 않았으면"'''
        zone: 'Zone|None' = None
        def __init__(self, effect: Effect, *index):
            super().__init__(effect, *index)
        
        def check(self, in_action: Action|bool):
            if not self.zone:
                raise AttributeError
            return super().check(in_action) and \
                   self.zone.is_for_current_player() and \
                   self.effect.board.turn_end and \
                   not self.zone.has_been_let and \
                   not self.effect.is_reserved()
        
        def give_parameter(self, param: dict | None):
            return {'zone': self.zone}


    def __init__(self, halfboard:'HalfBoard'):
        super().__init__(halfboard)
        self.name = 'error: not specific zone'
        self.has_been_let = False
        self.Collapse = type('Collapse', (Zone.Collapse,), {'zone': self})
        self._ZoneCollapseCondition = type(
            '_ZoneCollapseCondition', (Zone._ZoneCollapseCondition,), {'zone': self}
        )

    def on_top(self):
        if not self.is_empty():
            return self._cards[-1]
        else:
            return None

class MainZone(Zone):
    class MainZoneCollapse(Zone.Collapse):
        def process(self):
            super().process()
            raise Board.End
        
    class _LetEffect(Effect):
        class _MainZoneLetCondition(Condition):
            '''"자기 턴이고" "턴이 끝나지 않았으면"'''
            def check(self, in_action):
                return super().check(in_action) and \
                       self.effect.bind_to.is_for_current_player() and \
                       not self.effect.bind_to.halfboard.board.turn_end
            
        class _MainZoneLetAction(Zone.Let):
            '''Let 후 turn_end 활성화'''
            def generate(self, card:Card|None=None):
                if card:
                    self.card = card
                if not self.card:
                    raise Exception('No card to Let!')
            
            def process(self):
                result = super().process()
                self.effect.board.turn_end = True
                return result
        
        def __init__(self, bind_to:'MainZone'):
            super().__init__(bind_to)
            self.bind_to = bind_to
            self.effectblocks = [
                self._MainZoneLetCondition(self, 1, None),
                bind_to._DragIntoPackChoice(self, 2, None),
                _GetCardActiveCondition(self, None, 3, 3),
                self._MainZoneLetAction(self, None, None, destination=self.bind_to)
            ]

    class _MainZoneCollapseEffect(Effect):
        bind_to: 'MainZone'
            
        def __init__(self, bind_to: 'MainZone'):
            super().__init__(bind_to)
            self.effectblocks = [
                self.bind_to._ZoneCollapseCondition(self, 1),
                self.bind_to.MainZoneCollapse(self)
            ]
            
    def __init__(self, halfboard:'HalfBoard'):
        super().__init__(halfboard)
        self.name = f"{self.halfboard.name}'s Main Zone"
        self.let = self._LetEffect(self)
        self.effects.append(self.let)

class SubZone(Zone):
    class SubZoneCollapse(Zone.Collapse):
        zone: 'SubZone'
        def process(self):
            result = super().process()
            if result == True:
                self.zone.row.remove(self.zone)
                del self.zone
            return result
        
    class _LetEffect(Effect):
        bind_to: 'SubZone'
        class _InitLetCondition(Condition):
            '''"Idle이면서" "초기화 전이면"'''
            effect: 'SubZone._LetEffect'
            def check(self, in_action:Action|None):
                if not in_action and self.effect.bind_to.init_card:
                    print(f'Init card {self.effect.bind_to.init_card} in {self.effect.bind_to}.')
                    return True
                else:
                    return False
                
            def give_parameter(self, param: dict | None):
                return {'card': self.effect.bind_to.init_card}
                    
        class _SubZoneLetCondition(Condition):
            '''"자기 턴이면"'''
            def check(self, in_action):
                return super().check(in_action) and \
                       self.effect.bind_to.is_for_current_player()
            
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
            self.effectblocks = [
                self._SubZoneLetCondition(self, 1, None),
                self._InitLetCondition(self, 3, 2),   # Pass Choice if Init.
                bind_to._DragIntoPackChoice(self, 3, None),
                self._SubZoneLetAction(self, destination=self.bind_to)
            ]

    class _SubZoneCollapseEffect(Effect):
        bind_to: 'SubZone'
        class _SubZoneCollapseCondition(Condition):
            '''"비어 있음" "초기화 끝남"'''
            effect:'SubZone._SubZoneCollapseEffect'
            def check(self, in_action:Action|bool) -> bool | int:
                return super().check(in_action) and \
                       self.effect.bind_to.is_empty() and \
                       not bool(self.effect.bind_to.init_card)
            
            def give_parameter(self, param: dict | None):
                return {'zone': self.effect.bind_to}
            
        def __init__(self, bind_to: 'Zone'):
            super().__init__(bind_to)
            self.effectblocks = [
                self._SubZoneCollapseCondition(self, 2, 1),
                self.bind_to._ZoneCollapseCondition(self, 2),
                self.bind_to.SubZoneCollapse(self)
            ]
    
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

    def rename(self):
        self.index = self.row.subzones.index(self)
        self.name = f"{self.halfboard.name}'s Sub Zone {self.index}"

class Row(GameComponent):
    class Deploy(Action):
        row: 'Row|None' = None
        card: 'Card|None' = None
        new_index: int|None = None

        def generate(self, subzone_index:int, card:Card):
            self.card = card
            self.new_index = subzone_index
            super().generate()

        def process(self):
            if not self.card or not self.row or self.new_index == None:
                raise AttributeError
            super().process()
            new_subzone = self.row.create_subzone(self.new_index)
            new_subzone.init_card = self.card
            self.state = 'resolved'
            return True

    class _DeployEffect(Effect):
        bind_to: 'Row'

        class _DeployRowCondition(Condition):
            '''"subzone이 3개 미만이면"'''
            effect: 'Row._DeployEffect'
            def check(self, in_action:Action|bool):
                return super().check(in_action) and \
                       self.effect.bind_to.is_for_current_player() and \
                       bool(len(self.effect.bind_to.subzones) < 3)

        class _TempZoneChoice(Choice):
            subzone_index: int
            def __init__(self, effect:Effect, *index):
                super().__init__(effect, *index, key='temp zone')

            def match(self, key:GameComponent|str, index:int|None):
                if isinstance(self.effect.board.holding, Card) and self.key == key and \
                   self.effect.bind_to.is_for_current_player():
                    if index:
                        self.subzone_index = index - 1
                    else:
                        raise Exception('No index while Deploying!')
                    return True
                else:
                    return False
                
            def give_parameter(self, param):
                return {'card': self.effect.board.holding,
                        'subzone_index': self.subzone_index}

        def __init__(self, bind_to:'Row'):
            super().__init__(bind_to)
            self.effectblocks = [
                self._DeployRowCondition(self, 1, None),
                self._TempZoneChoice(self, 2, None),
                _GetCardActiveCondition(self, None, 3, 3),
                self.bind_to.Deploy(self)
            ]

    def __init__(self, halfboard:'HalfBoard'):
        self.halfboard = halfboard
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
'''GameComponents End'''

class HalfBoard(GameComponent):
    _board: 'Board'
    cardlist: list[type[Card]] = []

    class _LoseAction(Action):
        def __init__(self, effect: Effect, loser:'HalfBoard'):
            super().__init__(effect)
            self.loser = loser

        def process(self):
            super().process()
            print(f'Due to: {self.effect}')
            self.effect.board.loser = self.loser
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
            raise Exception('No Board for HalfBoard!')

    def get_suborder(self):
        return len(self.row.subzones)

    def get_loseaction(self, effect:Effect):
        return self._LoseAction(effect, self)

class Board(GameComponent):
    class End(Exception):
        pass

    class CoreEffect(Effect):
        class CoreRestriction(Restriction):
            '''"EffectBlock의 Effect가 유효할 것."'''
            def verify(self, eb:EffectBlock):
                if eb.effect.is_valid():
                    return True
                else:
                    return False
                
        def __init__(self, bind_to: 'Board'):
            super().__init__(bind_to)
            self.effectblocks = [
                self.CoreRestriction(self)
                ]
            
        def is_valid(self):
            '''Core rule은 언제나 valid.'''
            return True

    class InitialSetting(Effect):
        def __init__(self, board:'Board'):
            super().__init__(board)
            self.effectblocks: list[Action] = [
                board.player1.deck._DrawAction(self),
                board.player2.deck._DrawAction(self)
            ]

    def __init__(self, player1:HalfBoard, player2:HalfBoard):
        self.effects = []
        self.player1 = player1
        self.player2 = player2
        self.players = [player1, player2]
        self.loser = False
        self.current_player: HalfBoard = player1
        self.turn = 0
        self.turn_end = False
        self.action_stack: list[Action] = []
        self.restrictions: list[Restriction] = []

        for player in self.players:
            player._board = self

        self.holding: GameComponent|Choice|str|None = None
        self.holding_from = None
        self.gamecomponents: list[Board|HalfBoard|Row|Pack|Card] = []

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
        order.append(self.current_player)
        order.append(self.opponent())
        for player in [self.current_player, self.opponent()]:
            order.append(player.deck)
            order.append(player.graveyard)
            order.append(player.row)
            order.append(player.hand)
            order.append(player.main_zone)
            for zone in player.row.subzones:
                order.append(zone)
        for player in [self.opponent(), self.current_player]:
            if not player.main_zone.is_empty():
                order.append(player.main_zone.on_top())
            for zone in player.row.subzones:
                order.append(zone.on_top())
            if not player.graveyard.is_empty():
                order.append(player.graveyard.on_top())
        return order

    def initial_setting(self):
        '''시작 시 5장 뽑기. 여기서부터는 효과 처리가 필요하다.'''
        a = self.InitialSetting(self)
        for action in a.effectblocks:
            action.generate(num=5)
            action.process()

    def interpret(self, typ:Literal['click', 'drop'], keys:list[GameComponent|Choice|str], index:int|None=None):
        # Key selection
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
            
        for keytype in [Choice, str, Deck, Graveyard, Zone, Card, Row, HalfBoard, Board]:
            if keytype == Card:
                if key := key_searcher(keys, keytype, 'last'):
                    break
            else:
                if key := key_searcher(keys, keytype):
                    break
        
        if typ == 'click':
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
            if key == 'endbutton' and not self.turn%2:
                return key
            for choice in self.current_player.available_choices:
                if choice.match(key, index):
                    return choice
        else:
            raise Exception('Not click nor drop!')
        
        return False

    def drop_holding(self):
        print(f'you dropped {self.holding}.')
        self.holding = None
        self.holding_from = None

    def verify_restriction(self, eb:EffectBlock):
        for restriction in self.restrictions:
            if restriction.effect.is_valid():
                if not restriction.verify(eb):
                    print('restriction met!')
                    return False
            else:
                self.restrictions.remove(restriction)
        return True

    def add_action(self, action:Action, chain:bool=False):
        # 여기서 action 추가 순서 정함 (체인인지, 유발인지지)
        if chain:
            self.action_stack.insert(0, action)
        else:
            self.action_stack.append(action)

    def handle_effect(self, effect:Effect, choice:Choice|None=None, in_action:Action|bool=False):
        # Init
        effectblock = None
        resume = False
        param = None

        # Can restart EffectBlock chain from Choice.
        if choice:
            resume = True
            effect = choice.effect
            for eb in effect.effectblocks:
                # Regard there's no Choice reuse in single Effect.
                if eb == choice:
                    effectblock = eb
                    break
            if not effectblock:
                raise Exception('No matching effectblock for choice!')
        # Else, start from beginning.
        else:
            if isinstance(in_action, Action) and effect == in_action.effect:
                print(f'{effect} is Self-Triggered. Ignore.')
                return False
            effectblock = effect.effectblocks[0]

        # Run each EffectBlock
        while effectblock:
            eb = effectblock
            # Check each EffectBlock with current restrictions.
            if not self.verify_restriction(eb):
                if choice:
                    print('Your choice could not pass restriction.')
                return False
            if param:
                eb.add_parameter(param)
            # Conditions
            if isinstance(eb, Condition):
                result = eb.check(in_action)
                effectblock = eb.get_next_effblock(result)
                if not effectblock and choice:
                    print(f'Your choice could not pass condition {eb}.')

            # Restrictions
            elif isinstance(eb, Restriction):
                if eb not in self.restrictions:
                    self.restrictions.append(eb)
                effectblock = eb.get_next_effblock(True)
            # Choices
            elif isinstance(eb, Choice):
                if not resume:
                    self.current_player.available_choices.append(eb)
                    return True
                else:
                    effectblock = eb.get_next_effblock(True)
                    resume = False
            # Actions
            elif isinstance(eb, Action):
                if param:
                    eb.generate(**param)
                    param = None
                else:
                    eb.generate()
                self.action_stack.append(eb)
                print(f'Action {eb} appended.')
                return True
            else:
                raise Exception('Not right EffectBlock!')
            
            param = eb.give_parameter(param)

    def search_effect(self, in_action:Action|bool=False):
        # Search Mode: In action or Idle.
        for gamecomponent in self.refresh_gamecomponents():
            for effect in gamecomponent.effects:
                if self.handle_effect(effect, in_action=in_action) == 'end':
                    raise self.End

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
                # Init
                self.turn_end = False
                self.turn += 1
                self.current_player = self.player1 if self.turn%2 else self.player2
                print('start turn')
                self.action_stack = []
                self.current_player.available_choices = []
                self.opponent().available_choices = []

                # Init
                for player in self.players:
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
                        # Action stack is not empty.
                        while len(self.action_stack) > 0:
                            current_action = self.action_stack[0]
                            print(f'Current Action:{current_action}. ', end="")
                            # Valid Action
                            if current_action.effect.is_valid():
                                print('Start searching chain.')
                                self.search_effect(current_action)  # Trigger Mode
                                # Action was kept; No Chain.
                                if current_action == self.action_stack[0]:
                                    print('No chain.')
                                    # Passes restriction.
                                    if self.verify_restriction(current_action):
                                        print('processing...')
                                        result = current_action.process()
                                        # current_ action has other actions to be handled first.
                                        if isinstance(result, Action):
                                            print(f'Action {current_action} has prior action {result}.')
                                            self.add_action(result, True)
                                            continue
                                        # else. current_action is normally done.
                                    
                                    # Doesn't pass restriction -> Nothing happens.
                                    else:
                                        print("Action couldn't pass restriction.")
                                    # action removal.
                                    print(f"{current_action} is removed.")
                                    self.action_stack.remove(current_action)
                                # If Action changed, run another search. pass.
                                else:
                                    print(f'Chain {self.action_stack[0]} found. Run another Search.')
                            # Invalid Action
                            else:
                                print('But From Invalid Effect. Erase.')
                                self.action_stack.remove(current_action)
                           
                        # There are no action. Run idle search.
                        print('Action stack emptied.')
                        # Chain is over; No holding card.
                        self.drop_holding()
                        # Initialize choices.
                        self.current_player.available_choices = []
                        print('Try Idle Search.')
                        self.search_effect()    # Idle Mode
                        # Escape if there's still no action.
                        if len(self.action_stack) == 0:
                            running = False

                    # From here, no chain.

                    # Check turn end here. If changed, break.
                    if self.turn_end:
                        continue

                    # Else, Player choose what to do.
                    print('No Idle Action. Can choose now.')
                    chossing = True
                    while chossing:
                        args: tuple[Literal['click', 'drop'], list, int|None] = yield
                        print('got message')
                        if type(args) == tuple:
                            typ, keys, index = args
                            if (typ == 'click' or typ == 'drop') and isinstance(keys, list):
                                choice = self.interpret(typ, keys, index)
                            # If not valid choice, reset the holding card.
                            if choice == False:
                                self.drop_holding()
                            # If choice is valid, break. Give the output action to the stack.
                            elif isinstance(choice, Choice):
                                print(f'your choice is {choice}.')
                                chossing = False
                                self.handle_effect(choice.effect, choice)
                            elif choice == 'endbutton':
                                self.turn_end = True
                                chossing = False
                        else:
                            print('Not a right type of yield!')
                    # Go back to idle state

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
#   input player 1, 2 {name, deck, etc}
#   player1 = HalfBoard('Player 1')
#   player2 = HalfBoard('Player 2')
#   game = Board(player1, player2)
#   game.play()