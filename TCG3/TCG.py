from typing import Literal, Type, Generator, Union

CANCEL = 'Cancel'

LOSE = 'LOSE'
DONE = 'DONE'
PROCESSRESULT = Literal['LOSE', 'DONE']

CHOICELIST = list['GameComponent']
CHOICEDICT = dict['Effect', CHOICELIST]

INPUTTYPE = Union['GameComponent', Literal['Cancel'], None]

COLORTYPE = Literal['R', 'Y', 'B']
EFFECTTYPE = Literal['StateTrigger', 'EffectTrigger', 'Declare']
TAGS = EFFECTTYPE|COLORTYPE


class Player:
    _cardlist : list['Card'] = []

    def __init__(self, name:str) -> None:
        self._name = name

    def game_init(self, game:'Game'):
        self._game = game
        for card in self._cardlist:
            card._game = game

    @property
    def name(self):
        return self._name

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
    
    def __init__(self, parent:'Card|Game') -> None:
        self.parent = parent
        if isinstance(self.parent, Game):
            self.game = self.parent
        else:
            self.game = self.parent.game

        self._activated = False
        self.checker = self._checker()
        self.processor = self._processor()

    def _checker(self) -> Generator[CHOICELIST, INPUTTYPE, None]:
        while None:
            yield
        return None

    def check(self, input:INPUTTYPE) -> CHOICELIST|None:
        try:
            return self.checker.send(input)
        except StopIteration as e:
            resolution = e.value
            return resolution

    def _processor(self) -> Generator[CHOICELIST|CHOICEDICT, INPUTTYPE, PROCESSRESULT]:
        while None:
            yield
        return DONE

    def process(self, input:INPUTTYPE) -> CHOICELIST|CHOICEDICT|PROCESSRESULT:
        try:
            return self.processor.send(input)
        except StopIteration as e:
            resolution = e.value
            assert resolution == DONE or resolution == LOSE
            if resolution == DONE:
                self.processor = self._processor()
            return resolution

    def _settype(self, *typ:Literal['StateTrigger', 'EffectTrigger', 'Declare']):
        self._tags = self._tags.difference({'StateTrigger', 'EffectTrigger', 'Declare'})
        self._tags = self._tags.intersection(typ)

    @property
    def tags(self):        
        return self._tags
    
    @property
    def activated(self):
        return self._activated
    
    @property
    def needs_check(self):
        return True if hasattr(self, 'check') else False

class Card(GameComponent):
    _name : str = "Dummy"
    _power : int|None = None
    _color : COLORTYPE|None = None
    _description : str = ''
    _location : 'Pile|None' = None
    _owner : Player
    _effectclasses : list[Type[Effect]] = []

    def __init__(self, owner:Player) -> None:
        self._owner = owner
        self._effects : list[Effect] = []
        for effcls in self._effectclasses:
            self._effects.append(effcls(self))

    @property
    def name(self):
        return self._name

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
    
    @property
    def image(self):
        return None
    
    @property
    def description(self):
        return self._description
    
    @property
    def game(self):
        return self._game

    def covered_type(self):
        if not self.location or isinstance(self.location, Deck):
            return 'full'
        elif isinstance(self.location, Hand):
            return 'hidden'
        elif isinstance(self.location, Column) and self.location.cards[0] is not self:
            return 'half'
        else:
            return 'none'

class Creature(Card):
    pass

class Spell(Card):
    pass

class Pile(GameComponent):
    def __init__(self, game:'Game', name: str, owner:Player|None=None) -> None:
        super().__init__(game, name, owner)
        self._cards : list[Card] = []

    @property
    def cards(self):
        return self._cards
    
    @property
    def length(self):
        return len(self._cards)

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
        def _checker(self):
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

    class DeclareRule(Effect):
        def check(self):
            return None
        
        def _processor(self) -> Generator[CHOICELIST|CHOICEDICT, INPUTTYPE, PROCESSRESULT]:
            eff_dict = self.game.get_declaritive_effects()
            while eff_dict:
                gc = yield eff_dict
                if not isinstance(gc, GameComponent):
                    return DONE
                potent_eff_dict : dict[Effect, list[GameComponent]] = {eff:[] for eff in eff_dict if gc in eff_dict[eff]}
                for eff in potent_eff_dict:
                    result = eff.check(gc)
                    if not isinstance(result, list):
                        raise Exception('If drag is possible drop is possible!')
                    potent_eff_dict[eff] = result
                
                gc = yield potent_eff_dict
                if not isinstance(gc, GameComponent):
                    return DONE
                final_effs = [eff for eff in potent_eff_dict if gc in potent_eff_dict[eff]]
                for eff in final_effs:
                    result = eff.check(gc)
                    if isinstance(result, list):
                        eff_dict = {eff: result}
                    else:
                        return DONE

            return LOSE

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
        self.rules : list[Effect] = [self.DestroyRule(self), self.DrawRule(self), self.LetRule(self), self.DeclareRule(self)]

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

    def get_declaritive_effects(self):
        idle_choices : dict[Effect, list[GameComponent]]= {}
        for effect in self.get_effects():
            result = effect.check(None)
            if type(result) == list:
                idle_choices[effect] = result
        return idle_choices

    def get_next_active_effect(self):
        all_effects = self.get_effects()
        for effect in all_effects:
            effect.check(None)
        active_effects = [effect for effect in all_effects if effect.activated]
        return active_effects[0] if active_effects else None

    def check_turn_end(self):
        if self.tot_power(self.current_player) > self.tot_power(self.opponent()):
            self.current_player = self.opponent()
            return True
        else:
            return False

    def run(self):
        yield 'Game start'

        # Game Loop
        while True:
            yield 'Turn starts.'

            # Turn Loop
            while True:
                rightmost_effect = None

                # Effect Selection Loop
                while True:

                    rightmost_effect = self.get_next_active_effect()
                    if self.executing is rightmost_effect:
                        break
                    else:
                        self.executing = rightmost_effect

                # Rightmost Activated Effect
                if self.executing:
                    responce = None

                    # Process Loop
                    while True:
                        if responce == CANCEL:
                            result = self.executing.process(CANCEL)
                        else:
                            result = self.executing.process(responce)
                        if result is False:
                            return self.current_player
                        elif result is True:
                            break
                        elif isinstance(result, list):
                            responce = yield {self.executing:result}
                        elif isinstance(result, dict):
                            responce = yield result
                        else:
                            raise Exception('Wrong type of result!')
                # No Active Effect
                else:
                    return self.current_player
                
                if self.check_turn_end():
                    break
        
    def IO(self) -> Generator[CHOICEDICT|str, INPUTTYPE, Player]:
        game = self.run()
        yield 'Game Start'

        try:
            message = None

            while True:
                responce = game.send(message)
                if isinstance(responce, str):
                    yield responce
                else:
                    message = yield responce

        except StopIteration as e:
            self.loser = e.value
            return self.loser
