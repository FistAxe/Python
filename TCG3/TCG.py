from typing import Literal, Type, Generator, Any

CANCEL = 'Cancel'

COLORTYPE = Literal['R', 'Y', 'B']
EFFECTTYPES = Literal['StateTrigger', 'EffectTrigger', 'Declare']
TAGS = EFFECTTYPES|COLORTYPE


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
    _activated : bool = False
    _tags : set[TAGS] = set()
    game : 'Game'
    param : dict[str, int|GameComponent|list[GameComponent]|tuple[GameComponent]]
    
    def __init__(self, parent:'Card|Game') -> None:
        self.parent = parent
        if isinstance(self.parent, Game):
            self.game = self.parent
        else:
            self.game = self.parent.game

    def check(self, drag:GameComponent|None, drop:GameComponent|None) -> bool|list[GameComponent]:
        return False

    def process(self, gc:GameComponent|None) -> bool|list[GameComponent]:
        return False
    
    def _settype(self, *typ:Literal['StateTrigger', 'EffectTrigger', 'Declare']):
        self._tags = self._tags.difference({'StateTrigger', 'EffectTrigger', 'Declare'})
        self._tags = self._tags.intersection(typ)

    @property
    def tags(self):        
        return self._tags
    
    @property
    def activated(self):
        return self._activated
    
    @activated.setter
    def activated(self, b:bool):
        self._activated = b

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
        self.rules : list[Effect] = [self.DestroyRule(self), self.DrawRule(self), self.LetRule(self)]

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

    def get_effects(self):
        return self.rules + [effect for card in self.cards() for effect in card.effects]

    def check_effects(self, effects:list[Effect]|None=None, in_chain:bool=False, drag:GameComponent|None=None, drop:GameComponent|None=None):
        if not in_chain:
            idle_choices : dict[Effect, list[GameComponent]]= {}
        effs = effects if effects else self.get_effects()
        for effect in effs:
            result = effect.check(drag, drop)
            if type(result) == list and not in_chain:
                idle_choices[effect] = result
            elif result is True:
                effect.activated = True
        return idle_choices if not in_chain else None

    def get_first_active_effect(self):
        active_effects = [effect for effect in self.get_effects() if effect.activated]
        return active_effects[0] if active_effects else None

    def run(self):
        yield 'Game start'

        while True:
            yield 'Turn starts.'

            while self.tot_power(self.current_player) <= self.tot_power(self.opponent()):
                while (last_chain := self.get_first_active_effect()) is not self.executing:
                    self.executing = last_chain
                    self.check_effects(in_chain=True)

                if last_chain:
                    responce = None
                    while True:
                        result = last_chain.process(responce)
                        if isinstance(result, bool):
                            break
                        else:
                            responce = yield {last_chain:result}

                #manual
                elif (choices := self.check_effects(in_chain=False)):
                    while self.get_first_active_effect():
                        responce = yield choices
                        possible_choices = [key for key, value in choices.items() if responce in value]
                        choices = self.check_effects(effects=possible_choices, drag=responce)
                        if not choices:
                            raise Exception('If drag is possible drop is possible!')
                        responce = yield choices
                        possible_choices = [key for key, value in choices.items() if responce in value]
                        choices = self.check_effects(effects=possible_choices, drop=responce)
                        if not choices:
                            break

                #No Action
                else:
                    return self.current_player
        
    def IO(self) -> Generator[dict|str|None, GameComponent, StopIteration]:
        game = self.run()

        try:
            message = None
            while True:
                responce = None
                while isinstance(responce, str):
                    responce = game.send(message)
                    yield responce
                message = yield

        except StopIteration as e:
            return e
