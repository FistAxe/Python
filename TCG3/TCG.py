from typing import Literal, Type, Generator

CANCEL = 'Cancel'

COLORTYPE = Literal['R', 'Y', 'B']
EFFECTSTATES = Literal['Idle', 'Pending', 'Executing']
EFFECTTYPES = Literal['StateTrigger', 'EffectTrigger', 'Declare']
TAGS = EFFECTSTATES|EFFECTTYPES|COLORTYPE


class Player:
    def __init__(self, name:str) -> None:
        self._name = name
        self._cardlist : list['Card'] = []

    def game_init(self, game:'Game'):
        self._game = game
        for card in self._cardlist:
            card._game = game

class GameComponent:
    def __init__(self, game:'Game', name:str, owner:Player|None=None) -> None:
        self._game = game
        self._name = name
        self._owner = owner

    @property
    def game(self):
        return self._game
    
    @property
    def owner(self):
        return self._owner

class Effect:
    _tags : set[TAGS] = set()
    game : 'Game'
    _generator : Generator[list|None, GameComponent|None, None]
    
    def __init__(self, parent:'Card|Game') -> None:
        self.parent = parent
        if isinstance(self.parent, Game):
            self.game = self.parent
        else:
            self.game = self.parent.game
        self._init()

    def _init(self):
        self._generator = self._gen()

    def run(self, gc:GameComponent|None) -> 'Effect|list[GameComponent]|None':
        return self._generator.send(gc)
    
    def _gen(self) -> Generator[list[GameComponent]|None, GameComponent|None, None]:
        raise NotImplementedError
    
    def _settype(self, *typ:Literal['StateTrigger', 'EffectTrigger', 'Declare']):
        self._tags = self._tags.difference({'StateTrigger', 'EffectTrigger', 'Declare'})
        self._tags = self._tags.intersection(typ)

    @property
    def tags(self):
        state = None

        if self._tags & {'Idle', 'Pending', 'Executing'}:
            raise Exception('Defined State in Tags!')
        
        in_que = self in self.game.event_que
        if in_que:
            state = 'Idle'
        elif self is not self.game.executing:
            state = 'Pending'
        else:
            state = 'Executing'
        
        return self._tags & set(state)

class Card(GameComponent):
    _name : str = "Dummy"
    _power : int|None = None
    _color : COLORTYPE|None = None
    _location : 'Pile|None' = None
    _owner : Player
    _effectclasses : list[Type[Effect]] = []

    def __init__(self, game:'Game', owner:Player) -> None:
        super().__init__(game, self._name, owner)
        self._effects : list[Effect] = []
        for effcls in self._effectclasses:
            self._effects.append(effcls(self))

    @property
    def power(self):
        return self._power
    
    @property
    def color(self):
        return self._color
    
    @property
    def location(self):
        return self._location
    
    @property
    def effects(self):
        return self._effects

    def covered_type(self):
        if not self.location or isinstance(self.location, Deck) or isinstance(self.location, Hand):
            return 'full'
        elif isinstance(self.location, Column) and self.location.cards[0] is not self:
            return 'half'
        else:
            return 'none'

class Pile(GameComponent):
    def __init__(self, game:'Game', name: str, owner:Player|None=None) -> None:
        super().__init__(game, name, owner)
        self._cards : list[Card] = []

    @property
    def cards(self):
        return self._cards

class Deck(Pile):
    pass

class Graveyard(Pile):
    pass

class Hand(Pile):
    pass

class Column(Pile):
    def col_power(self, player:Player):
        pow = 0
        for card in self.cards:
            if card.owner is player and card.power:
                pow += card.power
        return pow

class Row(GameComponent):
    def __init__(self, game:'Game', name:str) -> None:
        super().__init__(game, name)
        self._columns : list[Column] = []

    @property
    def columns(self):
        return self._columns

class Event:
    def __init__(self, parent) -> None:
        self.parent = parent

    def execute(self):
        pass

class Game:
    class DrawRule(Effect):
        pass

    class LetRule(Effect):
        def _gen(self):
            self._settype('Declare')
            possible_let_dict : dict[Card, list[Column]] = {}
            for card in self.game.hand[self.game.current_player].cards:
                possible_places = self.lettable(card)
                if possible_places:
                    possible_let_dict[card] = possible_places
            card = None
            while True:
                card = yield list(possible_let_dict.keys())

                if isinstance(card, Card) and card in possible_let_dict:
                    possible_places = possible_let_dict[card]
                    column = yield possible_places

                    if column in possible_places:
                        assert isinstance(column, Column)
                        break
                    elif column == CANCEL:
                        yield None
                    else:
                        raise Exception
            
            yield self
            self._let(card, column)
            while 'Executing' in self.tags:
                yield None
            return None

        def _let(self, card, column):
            pass

        def lettable(self, card:Card):
            pass

    class DestroyRule(Effect):
        pass

    def __init__(self, player1:Player, player2:Player) -> None:
        self._players = [player1, player2]
        self.current_player : Player = self._players[0]

        for player in self._players:
            player.game_init(self)

        self.row = Row(self, 'Row')
        self.deck = {self._players[0] : Deck(self, 'Deck 1', self._players[0]),
                     self._players[1] : Deck(self, 'Deck 2', self._players[1])}
        self.graveyard = {self._players[0] : Graveyard(self, 'Graveyard 1', self._players[0]),
                     self._players[1] : Graveyard(self, 'Graveyard 2', self._players[1])}
        self.hand = {self._players[0] : Hand(self, 'Hand 1', self._players[0]),
                     self._players[1] : Hand(self, 'Hand 2', self._players[1])}
        self.rules = [self.DestroyRule(self), self.DrawRule(self), self.LetRule(self)]

        self.effect_que: list[Effect] = []
        self.executing : Effect|None = None

    @property
    def players(self):
        return [self.current_player, self.opponent()]
    
    def opponent(self, player:Player|None=None):
        if player is None:
            player = self.current_player
        
        if player == self._players[0]:
            return self._players[1]
        elif player == self._players[1]:
            return self._players[0]
        else:
            raise ValueError

    def cards(self):
        cards : list[Card] = []
        reverse = False
        if self.current_player is self._players[1]:
            reverse = True
        ordered_columns = reversed(self.row.columns) if reverse else self.row.columns
        for column in ordered_columns:
            cards.extend(list(reversed(column.cards)))
        return cards

    def tot_power(self, player:Player):
        return sum(column.col_power(player) for column in self.row.columns)

    def search_effects(self, *efftypes:EFFECTTYPES, and_or:Literal['and', 'or']='and'):
        def _classifier(effect, effsets, and_or):
            if not efftypes:
                return True
            elif and_or == 'and':
                return all(tag in effect.tags for tag in effsets)
            elif and_or == 'or':
                return bool(effect.tags & effsets)
            return False
    
        effectlist : list[Effect] = []
        choices : dict[Effect, list] = {}
        efftypes_set = set(efftypes)
        effectlist.extend(self.rules)
        for effects in [card.effects for card in self.cards()]:
            for effect in effects:
                if _classifier(effect, efftypes_set, and_or):
                    effectlist.append(effect)
        
        for effect in effectlist:
            result = effect.run(None)
            if isinstance(result, Effect):
                return result
            elif isinstance(result, list):
                choices[effect] = result
        return choices

    def run(self):
        result = None

        yield 'Game start'

        while True:
            yield 'Turn starts.'

            while self.tot_power(self.current_player) <= self.tot_power(self.opponent()):
                if not result:
                    result = self.search_effects()
                
                #automatic
                if isinstance(result, Effect):
                    if self.effect_que[-1] is not result:
                        self.effect_que.append(result)
                    elif self.effect_que:
                        result = self.effect_que[-1].run(None)
                        self.effect_que.pop()
                    continue

                #manual
                elif result:
                    responce = None
                    while isinstance(responce, Choice):
                        yield result
                        responce = yield
                        if not isinstance(responce, Choice):
                            yield 'Wrong Choice!'
                    assert isinstance(responce, Choice)
                    result = responce.parent.send(responce)
                    if isinstance(result, Choice):
                        result = [result]

                #No Action
                else:
                    return self.current_player
        
    def IO(self) -> Generator[list[Choice]|str|None, Choice, StopIteration]:
        game = self.run()

        try:
            while True:
                responce = None
                while isinstance(responce, str):
                    responce = game.send(message)
                    yield responce
                message : Choice = yield

        except StopIteration as e:
            return e
