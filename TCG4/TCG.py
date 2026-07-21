from enum import Enum, auto
from dataclasses import dataclass
from typing import Literal, Generator

class Keywords:
    pass

class BoardState(Keywords, Enum):
    IDLE = auto()
    SELECT = auto()
    SEARCHING = auto()
    EXECUTING = auto()
    INIT = auto()

class EffectState(Keywords, Enum):
    INACTIVE = auto()
    READY = auto()
    ACTIVE = auto()
    DONE = auto()

class ClickType(Keywords, Enum):
    CLICK = auto()
    DROP = auto()
    CANCEL = auto()
    """A cancel message."""

SELECT = BoardState.SELECT
SEARCHING = BoardState.SEARCHING
EXECUTING = BoardState.EXECUTING
INIT = BoardState.INIT
IDLE = BoardState.IDLE
INACTIVE = EffectState.INACTIVE
READY = EffectState.READY
ACTIVE = EffectState.ACTIVE
DONE = EffectState.DONE
CLICK = ClickType.CLICK
DROP = ClickType.DROP
CANCEL = ClickType.CANCEL

class PlayerInfo:
    def __init__(self, name, cardlist:list[type[Card]]):
        self.name = name
        self.cardlist = cardlist

class Effect:
    _stagetypes : list[type[Stage]]

    def __init__(self, source:GameObject) -> None:
        self._source = source

    @property
    def source(self):
        return self._source
    
    @property
    def is_in_chain(self):
        for stage in self.source.board.execution_stack:
            if stage.effect is self:
                return True
        return False
    
    def init(self) -> Stage|None:
        return self._stagetypes[0](self)

class Stage:
    def __init__(self, effect:Effect, **kwargs) -> None:
        self._effect = effect

    @property
    def effect(self):
        return self._effect
    
    def _get_stage(self, index:int, **kwargs):
        return self.effect._stagetypes[index](self.effect, **kwargs)

class TriggerStage(Stage):
    def __init__(self, effect: Effect):
        super().__init__(effect)

    def check(self) -> Stage|EffectState:
        return INACTIVE

class ChoiceStage(Stage):
    _choices: list[Choice]

    @property
    def choices(self):
        return self._choices

    def choose(self, choice:Choice) -> Stage|EffectState:
        return INACTIVE

class EventStage(Stage):
    def execute(self) -> Stage|EffectState:
        return DONE

class PlayerMovement(EventStage):
    pass

class Rule(Effect):
    def __init__(self, source:Board) -> None:
        self._source = source
        self._stages: list[Stage] = []
        for st in self._stagetypes:
            self._stages.append(st(self))

@dataclass
class Choice:
    choicestage: ChoiceStage
    click: GameObject
    drop: GameObject

class End:
    pass

class GameObject:
    def __init__(self, board:Board) -> None:
        self._board = board
        self._effects: list[Effect] = []

    @property
    def board(self):
        return self._board
    
    @property
    def effects(self):
        return tuple(self._effects)
    
class Card(GameObject):
    def __init__(self, board: Board, player:Player) -> None:
        super().__init__(board)
        self._player = player
        self._power: int|None = None

    @property
    def player(self):
        return self._player

    def get_power(self):
        return self._power if self._power else None

class Pile(GameObject):
    def __init__(self, board:Board) -> None:
        super().__init__(board)
        self._cards: list[Card] = []
    
    @property
    def cards(self):
        return self._cards

class OwnedPile(Pile):
    def __init__(self, board: Board, player:Player) -> None:
        super().__init__(board)
        self._player = player

    @property
    def player(self):
        return self._player

class Row(GameObject):
    def __init__(self, board: Board) -> None:
        super().__init__(board)
        self._cards: list[Card] = []

    @property
    def cards(self):
        return self._cards

class OwnedRow(Row):
    def __init__(self, board: Board, player:Player) -> None:
        super().__init__(board)
        self._player = player

    @property
    def player(self):
        return self._player

class InitiativeZone(GameObject):
    def __init__(self, board: Board) -> None:
        super().__init__(board)
        self._card: Card|None = None

    @property
    def card(self):
        return self._card

class Deck(OwnedPile):
    def init_add(self, card:Card):
        self._cards.append(card)

class Hand(OwnedPile):
    pass

class GraveYard(OwnedPile):
    pass

class ChainRow(Row):        
    pass

class OrderRow(OwnedRow):
    pass

class DrawRow(OwnedRow):
    pass

class Player(GameObject):
    def __init__(self, board:Board, playerinfo:PlayerInfo):
        super().__init__(board)
        self._name = playerinfo.name

    @property
    def name(self):
        return self._name
    
    @property
    def deck(self):
        return self.board.deck[self]
    
    @property
    def hand(self):
        return self.board.hand[self]
    
    @property
    def graveyard(self):
        return self.board.graveyard[self]
    
class Board:
    class TurnDrawRule(Rule):
        class TurnDrawTriggerStage(TriggerStage):
            def check(self):
                return self._get_stage(1)
        class TurnDrawChoiceStage(ChoiceStage):
            def __init__(self, effect: Effect) -> None:
                super().__init__(effect)
                self._choices = [
                    Choice(self, self.effect.source.board.current_player.deck,self.effect.source.board.current_player.deck)
                ]
            def choose(self):
                pass
        class TurnDrawEventStage(EventStage):
            pass
        _stagetypes = [
            TurnDrawTriggerStage,
            TurnDrawChoiceStage,
            TurnDrawEventStage
        ]

    def __init__(self, player1info:PlayerInfo, player2info:PlayerInfo):
        self._state: Keywords = INIT
        self._rules = [self.TurnDrawRule(self),]
        self._player1 = Player(self, player1info)
        self._player2 = Player(self, player2info)
        self._current_player: Player = self._player1

        self._rulelist: list[Rule] = []
        self._effectlist: list[Effect] = []
        self._choicelist: list[Choice] = []
        self._execution_stack: list[EventStage] = []

        self.deck: dict[Player, Deck] = {}
        self.hand: dict[Player, Hand] = {}
        self.graveyard: dict[Player, GraveYard] = {}
        self.chainrow = ChainRow(self)
        self.orderrow: dict[Player, OrderRow] = {}
        self.drawrow: dict[Player, DrawRow] = {}
        self.initiativezone = InitiativeZone(self)

        for player in self.players():
            self.deck[player] = Deck(self, player)
            self.hand[player] = Hand(self, player)
            self.graveyard[player] = GraveYard(self, player)
            self.orderrow[player] = OrderRow(self, player)
            self.drawrow[player] = DrawRow(self, player)
            
        for card in player1info.cardlist:
            self.deck[self._player1].init_add(card(self, self._player1))
        for card in player2info.cardlist:
            self.deck[self._player2].init_add(card(self, self._player2))

    @property
    def current_player(self):
        return self._current_player
    
    @property
    def effectlist(self):
        return tuple(self._effectlist)

    @property
    def choicelist(self):
        return self._choicelist if self._state is SELECT else None

    @property
    def execution_stack(self):
        return tuple(self._execution_stack)

    def opponent(self, player:Player|None=None):
        if not player:
            player = self.current_player
        return self._player2 if player is self._player1 else self._player1

    def players(self):
        return (self.current_player, self.opponent())
        
    def locations(self):
        return (self.initiativezone,
                self.chainrow,
                self.orderrow[self.opponent()],
                self.drawrow[self.opponent()],
                self.graveyard[self.opponent()],
                self.orderrow[self.current_player],
                self.drawrow[self.current_player],
                self.graveyard[self.current_player],
                self.hand[self.opponent()],
                self.hand[self.current_player],
                self.deck[self.opponent()],
                self.deck[self.current_player]
                )
    
    def cards(self):
        cards: list[Card] = []
        for location in self.locations():
            if isinstance(location, GraveYard) or isinstance(location, Hand) or isinstance(location, Row):
                cards.extend(location.cards)
            elif isinstance(location, InitiativeZone) and location.card:
                cards.append(location.card)
        return tuple(cards)
    
    def gameobjects(self):
        return self.locations() + self.cards()

    def _run(self) -> Generator[str | Keywords, tuple[GameObject, GameObject], End]:
        def refresh_effects() -> None:
            effects: list[Effect] = list(self._rulelist)
            effects.extend(
                effect
                for gameobject in self.gameobjects()
                for effect in gameobject.effects
            )
            self._effectlist = effects

        self._execution_stack = []
        self._choicelist = []
        choicestages: list[ChoiceStage] = []
        refresh_effects()

        # Turn Loop
        while True:
            self._current_player = self.opponent()
            self._state = IDLE

            # Event Loop
            while True:

                # Search Loop
                while True:
                    executing_stage = self._execution_stack[0] if self._execution_stack else None
                    choicestages = []

                    for effect in tuple(self._effectlist):
                        result = effect.init() # Let effects themselve handle recursive activation

                        if isinstance(result, EventStage):
                            self._execution_stack.insert(0, result)
                            continue

                        elif isinstance(result, ChoiceStage):
                            choicestages.append(result)

                    # Filled choicestages = Choice must be choosed BEFORE the execution
                    if choicestages:
                        self._choicelist = [
                            choice
                            for stage in choicestages
                            for choice in stage.choices
                        ]

                        self._choicedict = {
                            (choice.click, choice.drop): choice
                            for choice in self._choicelist
                        }

                        message = "Select!"
                        while True:
                            player_input = yield message
                            if player_input in self._choicedict:
                                player_choice = self._choicedict[player_input]
                                break
                            else:
                                message = "Wrong Selection!"
                        
                        next_stage = player_choice.choicestage.choose(player_choice)
                        if isinstance(next_stage, PlayerMovement):
                            pass
                        elif isinstance(next_stage, ChoiceStage):
                            

                # No legal movement and no pending execution means defeat.
                self._state = IDLE
                return End()
