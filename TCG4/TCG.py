from enum import Enum, auto
from dataclasses import dataclass
from typing import Literal, Generator, Self

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
        self._stage: Stage|None = None

    @property
    def source(self):
        return self._source
    
    @property
    def is_in_chain(self):
        for stage in self.source.board.execution_stack:
            if stage.effect is self:
                return True
        return False
    
    def get_stage(self) -> Stage|None:
        if self._stage:
            return self._stage
        else:
            return self._stagetypes[0](self)
        
    def init(self):
        self._stage = None

class Stage:
    def __init__(self, effect:Effect, **kwargs) -> None:
        self._effect = effect

    @property
    def effect(self):
        return self._effect
    
    def _get_next_stage(self, index:int, **kwargs):
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

    def choose(self, choice:Choice) -> Self|TriggerStage|EventStage|EffectState:
        return INACTIVE

class EventStage(Stage):
    def execute(self) -> Stage|EffectState:
        return DONE

class PlayerMovement(EventStage):
    pass

class Rule(Effect):
    def __init__(self, source:Board) -> None:
        self._source = source

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

        self.turn_start: bool = False

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
                return self._get_next_stage(1)
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

        # Game Start
        refresh_effects()

        # Turn Loop
        while True:
            self.current_player.turn_start = True
            # Execution Loop
            while True:
                confirmed_event = None

                # Searching Loop
                condition_changed: bool = True
                choicestages: list[ChoiceStage] = []
                while condition_changed:
                    condition_changed = False
                    if self.execution_stack:
                        pending_event = self.execution_stack[0]
                        loaded_effects: set[Effect] = set(eventstage.effect for eventstage in self.execution_stack)
                    else:
                        pending_event = None
                        loaded_effects = set()

                    for effect in self.effectlist:
                        if effect in loaded_effects:
                            continue
                        new_effectstage = effect.get_stage()
                        while isinstance(new_effectstage, TriggerStage):
                            new_effectstage = new_effectstage.check()
                        if isinstance(new_effectstage, EventStage):
                            self._execution_stack.insert(0, new_effectstage)
                            choicestages = []
                            condition_changed = True
                            break
                        elif isinstance(new_effectstage, ChoiceStage):
                            choicestages.append(new_effectstage)
                            condition_changed = True
                # pending_event, choicestages locked.

                # Choice Loop, if choicestages exist.
                if choicestages:
                    message = "Choose!"
                    multichoice: bool = False

                    # Multichoice Loop
                    while True:
                        # Initial Choiceset
                        if not multichoice:
                            self._choicelist = [
                                choice
                                for choicestage in choicestages
                                for choice in choicestage.choices
                            ]
                            self._choicedict = {
                                (choice.click, choice.drop) : choice
                                for choice in self._choicelist
                            }
                        # Get Input
                        click_and_drop = yield message
                        # Success
                        if click_and_drop in self._choicedict:
                            player_choice = self._choicedict[click_and_drop].choicestage
                            next_stage = player_choice.choose(self._choicedict[click_and_drop])
                            while isinstance(next_stage, TriggerStage):
                                next_stage = next_stage.check()
                            # Multichoice
                            if player_choice is next_stage:
                                multichoice = True
                                self._choicelist = player_choice.choices
                                self._choicedict = {(choice.click, choice.drop):choice for choice in self._choicelist}
                                message = "Choose More!"
                            # Movement
                            elif isinstance(next_stage, PlayerMovement):
                                confirmed_event = next_stage
                                break
                        # Fail and Multichoice
                        elif multichoice:
                            message = "Canceled! Choose Again."
                            multichoice = False
                        # Normal Fail
                        else:
                            message = "Wrong Choice! Choose Again."
                
                # Elif pending_event exists, make it valid_event.
                elif pending_event and pending_event is self.execution_stack[0]:    # No Execution Yet; Assert execution_stack if pending_event exists.
                    confirmed_event = pending_event
                    pending_event = None
                
                # Execution!
                if confirmed_event:
                    self._choicelist, choicestages = []
                    self._choicedict = {}
                    next_stage = confirmed_event.execute()
                    self._execution_stack.pop(0)
                    while isinstance(next_stage, TriggerStage):
                        next_stage = next_stage.check()
                    if isinstance(next_stage, EventStage):
                        self._execution_stack.insert(0, next_stage)
                    elif isinstance(next_stage, ChoiceStage):
                        pass
                    elif next_stage is DONE:
                        confirmed_event.effect.init()
                    refresh_effects()
                    # Turn check
                    if True:
                        self._current_player = self.opponent()
                        break
                
                # No Choice, No Event -> Lose!
                else:
                    return End()


