from typing import Literal, Type, Generator, Union, Any, TypedDict

class Lose(str):
    pass

class CheckPoint(str):
    pass

DONE = 'DONE'
PROCESSRESULT = Union[Lose, Literal['DONE']]

class Choice(TypedDict):
    action: str
    effect: 'Effect'
    source: 'GameComponent'
    target: 'GameComponent'

CANCEL = 'Cancel'
INPUTTYPE = Union['GameComponent', Literal['Cancel'], None]

COLORTYPE = Literal['R', 'Y', 'B']
EFFECTTYPE = Literal['Idle', 'Declarative']
TAGS = EFFECTTYPE|COLORTYPE|Literal['Rule']
STATES = Literal['CHECK', 'PENDING', 'IDLE', 'PROCESS', 'ACTIVATE', 'START']

class Player:
    _cardlist : list['Card'] = []

    def __init__(self, name:str) -> None:
        self._name = name

    def assign_game(self, game:'Game'):
        self._game = game

    @property
    def name(self):
        return self._name

    @property
    def game(self):
        return self._game

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
    _name = 'Effect'
    _tags : set[TAGS] = set()
    game : 'Game'
    
    def __init__(self, parent:'Card|Game') -> None:
        self.parent = parent
        if isinstance(self.parent, Game):
            self.game = self.parent
        else:
            self.game = self.parent.game

    @property
    def name(self):
        return self._name

    @property
    def tags(self):
        return self._tags
    
    @property
    def activated(self) -> bool:
        return False
    
    def activate(self, choice:Choice|None=None) -> list[Choice]|None:
        return None

    def process(self, choice:Choice|None=None) -> list[Choice]|PROCESSRESULT:
        return DONE
    
class Card(GameComponent):
    _name : str = "Dummy"
    _power : int|None = None
    _color : COLORTYPE|None = None
    _image : str = ''
    _description : str = ''
    _location : 'Pile|None' = None
    _owner : Player
    owner : Player
    _effectclasses : list[Type[Effect]] = []

    def __init__(self, owner:Player) -> None:
        self._owner = owner
        self._effects : list[Effect] = []
        for effcls in self._effectclasses:
            self._effects.append(effcls(self))

    @property
    def name(self):
        return self._name if self._is_loc_revealed('top') else None

    @property
    def power(self):
        return self._power if self._is_loc_revealed('top') else None
    
    @property
    def color(self):
        return self._color if self._is_loc_revealed('top') else None
    
    @property
    def location(self):
        return self._location
    
    @property
    def effects(self):
        return self._effects if self._is_loc_revealed('bottom') else None
    
    @property
    def image(self):
        return self._image if self._is_loc_revealed('top') else None
    
    @property
    def description(self):
        return self._description if self._is_loc_revealed('top') else None
    
    @property
    def game(self):
        return self.owner.game

    def covered_type(self):
        if not self.location or isinstance(self.location, Deck):
            return 'full'
        elif isinstance(self.location, Hand):
            return 'hidden'
        elif isinstance(self.location, Column) and self.location.cards[0] is not self:
            return 'half'
        else:
            return 'none'
        
    def _is_loc_revealed(self, info_loc:Literal['top', 'bottom']):
        if self.covered_type() == 'hidden':
            assert isinstance(self.location, Hand)
            return True if self.game.current_player is self.location.owner else False
        elif self.covered_type() == 'none':
            return True
        elif self.covered_type() == 'full':
            return False
        elif self.covered_type() == 'half':
            return True if info_loc == 'top' else False

    def move(self, pile:'Pile'):
        if self._location:
            self._location.cards.remove(self)
        self._location = pile
        self._location.cards.append(self)
        
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
        self._new_column = Column(self.game, 'new column')

    @property
    def columns(self):
        return self._columns
    
    @property
    def new_column(self):
        return self._new_column if len(self.columns) < 6 else None

class Game:
    status : STATES

    class DrawRule(Effect):
        _tags = {'Rule'}
        _last_turn_drawed = 0
        _drawed = False

        @property
        def activated(self):
            if self._last_turn_drawed < self.game.turn:
                self._last_turn_drawed = self.game.turn
                self._drawed = False
            return True if not self._drawed else False
        
        def process(self, choice:Choice|None=None):
            if not choice:
                return [Choice(
                    action="PROCESS",
                    effect=self,
                    source=self.game.deck[self.game.current_player],
                    target=self.game.deck[self.game.current_player]
                )]

            try:
                draw_card = self.game.deck[self.game.current_player].cards[-1]
            except IndexError:
                return Lose('Could not draw from the deck.')
            draw_card.move(self.game.hand[self.game.current_player])
            self._drawed = True
            return DONE

    class LetRule(Effect):
        _tags = {'Rule'}
        _card = None
        _column = None

        @property
        def activated(self) -> bool:
            return True if self.game.status == 'IDLE' else False
        
        def process(self, choice:Choice|None=None):
            if self.game.status != 'IDLE':
                return False
            
            if not choice:
                choices : list[Choice] = []
                for card in self.game.hand[self.game.current_player].cards:
                    possible_columns = self.lettable(card)
                    if possible_columns:
                        for column in possible_columns:
                            choices.append(Choice(
                                action="PROCESS",
                                effect=self,
                                source=card,
                                target=column
                            ))
                return choices
            
            card, column = choice['source'], choice['target']
            if not isinstance(card, Card) or not isinstance(column, Column):
                raise Exception('Wrong activation!')
            card.move(column)
            return DONE

        def lettable(self, card:Card):
            if self.game.row.new_column:
                return self.game.row.columns + [self.game.row.new_column]
            else:
                return self.game.row.columns

    def __init__(self, player1:Player, player2:Player) -> None:
        self._players = [player1, player2]
        self.current_player : Player = self._players[0]
        self.lead_effect : Effect|None = None
        self.turn : int = 0

        self.row = Row(self, 'Row')
        self.deck = {self._players[0] : Deck(self, 'Deck 1', self._players[0]),
                     self._players[1] : Deck(self, 'Deck 2', self._players[1])}
        self.graveyard = {self._players[0] : Graveyard(self, 'Graveyard 1', self._players[0]),
                     self._players[1] : Graveyard(self, 'Graveyard 2', self._players[1])}
        self.hand = {self._players[0] : Hand(self, 'Hand 1', self._players[0]),
                     self._players[1] : Hand(self, 'Hand 2', self._players[1])}
        self.rules : list[Effect] = [self.DrawRule(self), self.LetRule(self)]

        for player in self._players:
            player.assign_game(self)
            for card in player._cardlist:
                card.move(self.deck[player])

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
        effects = self.rules
        for effs in [card.effects for card in self.cards() if card.effects]:
            effects.extend(effs)
        return effects

    def get_next_active_effect(self):
        active_effects = [effect for effect in self.get_effects() if effect.activated]
        if active_effects:
            return active_effects[0]
        else:
            return None

    def check_turn_end(self):
        if self.tot_power(self.current_player) > self.tot_power(self.opponent()):
            self.current_player = self.opponent()
            return True
        else:
            return False

    def get_choices(self, status: str) -> list[Choice]:
        all_choices : list[Choice] = []

        for effect in self.get_effects():
            if status =='PENDING' and effect.activated and (effect is self.lead_effect or 'Rule' in effect.tags):
                choices = effect.process()
                if isinstance(choices, list):
                    all_choices.extend(choices)
            
            if status in ('PENDING', 'IDLE'):
                choices = effect.activate()
                if isinstance(choices, list):
                    all_choices.extend(choices)
        
        return all_choices

    def run(self) -> Generator[list[Choice]|CheckPoint|str, Choice|Literal['Cancel']|None, Lose]:
        """A generator that runs the TCG game loop."""
        choices : list[Choice]
        choice : Choice|Literal['Cancel']|None

        for player in self.players:
            for _ in range(5):
                try:
                    draw_card = self.deck[player].cards[-1]
                except IndexError:
                    return Lose('Could not draw from the deck.')
                draw_card.move(self.hand[player])

        yield CheckPoint("Game Start")
        # Turn Loop
        while True:
            # Do turn start things
            self.turn += 1
            choice = None
            self.status = 'CHECK'
            yield 'TURN START'

            # Action Loop
            while True:
                yield f"---{self.status} STATE---"

                if self.status == 'CHECK':
                    while True:
                        new_lead_effect = self.get_next_active_effect()
                        if self.lead_effect is new_lead_effect:
                            yield f"Lead Effect Confirmed: {new_lead_effect}"
                            break
                        else:
                            self.lead_effect = new_lead_effect
                            yield f"Lead Effect change : {new_lead_effect}"
                        
                    self.status = 'PENDING' if self.lead_effect else 'IDLE'

                elif self.status in ('PENDING', 'IDLE'):
                    initial_choices = self.get_choices(self.status)
                    if not initial_choices:
                        return Lose('No choice available.')
                    else:
                        choices = initial_choices
                    
                    while True:
                        choice = yield choices
                        
                        if not choice:
                            choices = initial_choices
                        
                        elif choice == CANCEL:
                            self.status = 'CHECK'
                            break
                        
                        elif choice['action'] == 'PROCESS':
                            self.status = 'PROCESS'
                            break
                        
                        elif choice['action'] == 'ACTIVATE':
                            additional_choices = choice['effect'].activate(choice)  # Activation can have additional choices
                            if additional_choices:
                                choices = additional_choices
                            else:
                                self.status = 'CHECK'
                                break
                    
                    choices = []

                elif self.status == "PROCESS":
                    if not isinstance(choice, dict):
                        raise Exception
                    result = choice['effect'].process(choice)
                    if isinstance(result, Lose):
                        return result
                    elif result == DONE:
                        pass
                    else:
                        raise Exception('process should not have additional choices!')
                    
                    self.lead_effect = None
                    choice = None
                    self.status = "CHECK"

                    if self.check_turn_end():
                        break
        
    def IO(self) -> Generator[list[Choice]|str, GameComponent|Literal['Cancel']|None, Player]:
        command: Choice|Literal['Cancel']|None = None
        ui_input: GameComponent|Literal['Cancel']|None

        game = self.run()  # Start the game engine generator
        yield 'Game Engine Start'
        
        try:
            # Game Loop
            while True:
                # String Ignorance Loop
                while True:
                    ui_output = game.send(command)
                    if isinstance(ui_output, str):
                        yield ui_output
                        command = None
                    # Now list given
                    else:
                        choices = ui_output
                        break

                # Command Loop
                while not command:
                    selected_source: GameComponent|None = None
                    selected_target: GameComponent|None = None
                    
                    ui_input = yield choices
                    
                    if isinstance(ui_input, GameComponent) and ui_input in {c['source'] for c in choices}:
                        selected_source = ui_input
                    elif ui_input == 'Cancel':
                        command = CANCEL
                        print(f"Selected Choice: 'CANCEL'")

                    if not selected_source:  # If Canceled on Source Loop, back to the initial Choices
                        print("Got None in the first IO!")
                        continue

                    # Target Loop - Drop
                    choices_from_source = [c for c in choices if c['source'] is selected_source]
                    ui_input = yield choices_from_source
                        
                    # Cancel by drop -> No Meaning, back to Source Loop
                    if ui_input == 'Cancel' or ui_input is None:
                        continue
                        
                    possible_targets = {c['target'] for c in choices_from_source}
                    if ui_input in possible_targets:
                        selected_target = ui_input

                    # Source + Target -> Resolve
                    if selected_source and selected_target:
                        matching_choices = [c for c in choices_from_source if c['target'] is selected_target]

                        if not matching_choices:
                            print("IO Handler: Selection error. Resetting.")
                            continue

                        # Priority Warning
                        if len(matching_choices) > 1:
                            print(f"IO Handler WARNING: Ambiguous choices found, which violates game rules. "
                                f"Defaulting to the first one: {[c['effect'].name for c in matching_choices]}")
                        
                        command = matching_choices[0]
                        print(f"Selected Choice: '{command['effect'].name}'")

        except StopIteration as e:
            return e.value
