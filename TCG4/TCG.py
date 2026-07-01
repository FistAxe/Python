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

class Stage:
    def process(self) -> list[Choice]|Stage|Keywords:
        return INACTIVE
    
class ActionStage(Stage):
    pass

class TriggerStage(Stage):
    pass

class StaticStage(Stage):
    pass

class Effect:
    def __init__(self, source:GameObject) -> None:
        self._source = source
        self._stages: list[Stage] = []
        self._current_stage: Stage|None = None

    @property
    def source(self):
        return self._source
    
    @property
    def stages(self):
        return self._stages

    @property
    def current_stage(self):
        return self._current_stage
    
    def check(self) -> list[Choice]|Keywords|None:
        if not self.current_stage:
            result = self.stages[0].process()
        else:
            result = self.current_stage.process()
        
        if isinstance(result, Stage):
            self._current_stage = result
            return ACTIVE
        else:
            return result

@dataclass
class Choice:
    effect: Effect
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

class DamageZone(OwnedPile):
    pass

class ChainZone(Pile):
    pass

class Deck(OwnedPile):
    def init_add(self, card:Card):
        self._cards.append(card)

class Hand(OwnedPile):
    pass

class GraveYard(OwnedPile):
    pass

class Battleline(OwnedPile):
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
    
    @property
    def battleline(self):
        return self.board.battleline[self]
    
    @property
    def damagezone(self):
        return self.board.damagezone[self]

class Board:
    def __init__(self, player1info:PlayerInfo, player2info:PlayerInfo):
        self._state: Keywords = INIT
        self._rules = []
        self._player1 = Player(self, player1info)
        self._player2 = Player(self, player2info)
        self._current_player: Player = self._player1
        self._effectlist: list[Effect] = []
        self._choicelist: list[Choice] = []
        self._execution_stack: list[Effect] = []

        self.deck: dict[Player, Deck] = {}
        self.hand: dict[Player, Hand] = {}
        self.graveyard: dict[Player, GraveYard] = {}
        self.battleline: dict[Player, Battleline] = {}
        self.damagezone: dict[Player, tuple[DamageZone, DamageZone, DamageZone, DamageZone, DamageZone]] = {}
        self.chainzone = ChainZone(self)

        for player in self.players():
            self.deck[player] = Deck(self, player)
            self.hand[player] = Hand(self, player)
            self.graveyard[player] = GraveYard(self, player)
            self.battleline[player] = Battleline(self, player)
            self.damagezone[player] = (DamageZone(self, player),
                                       DamageZone(self, player),
                                       DamageZone(self, player),
                                       DamageZone(self, player),
                                       DamageZone(self, player))
            
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
    def event_que(self):
        return tuple(self._execution_stack)

    def opponent(self, player:Player|None=None):
        if not player:
            player = self.current_player
        return self._player2 if player is self._player1 else self._player1

    def players(self):
        return (self.current_player, self.opponent())

    def piles(self, player:Player|None=None):
        def _halfpiles(p:Player):
            return (p.battleline,
                    *p.damagezone,
                    p.graveyard,
                    p.deck,
                    p.hand
                    )
        if player:
            return _halfpiles(player)
        else:
            return (*_halfpiles(self.opponent()), *_halfpiles(self.current_player))

    def cards(self, player:Player|None=None):
        def _halfcards(player:Player):
            return (card for pile in self.piles(player) for card in pile.cards)

        return tuple(_halfcards(player)) if player else (*_halfcards(self.opponent()), *_halfcards(self.current_player))
        
    def gameobjects(self, player:Player|None=None):
        if player:
            return (
                    *self.piles(player),
                    *self.cards(player)
                    )
        else:
            return (
                    *self.piles(self.opponent()),
                    *self.cards(self.opponent()),
                    *self.piles(self.current_player),
                    *self.cards(self.current_player)
                    )

    def get_total_power(self, player:Player) -> int:
        if player not in self.players():
            raise Exception()
        power = 0
        for card in self.cards(player):
            p = card.get_power()
            if type(p) is int:
                power += p
        return power

    def _run(self) -> Generator[str|Keywords, tuple[GameObject, GameObject], End]:
        self._execution_stack = []

        #turn start
        while True:
            self._current_player = self.opponent()

            while True:
                # effect -> activation|choice|movement|inactivation
                # choice -> choice|movement
                # movement -> board refresh
                if self._state is SEARCHING:
                    self._choicelist = []
                    if self._execution_stack:
                        executing_eff = self._execution_stack[0]
                    else:
                        executing_eff = None
                
                    # execution stack search
                    for eff in self._effectlist:
                        result = eff.check()
                        if eff not in self._execution_stack and result is ACTIVE:
                            self._execution_stack.append(eff)
                        elif isinstance(result, list):
                            self._choicelist.extend(result)

                    # stack changed
                    if (not executing_eff and self._execution_stack) or \
                    (executing_eff is not self._execution_stack[0]):
                        continue
                    
                    # stack unchanged and loaded
                    elif executing_eff and executing_eff is self._execution_stack[0]:
                        self._state = EXECUTING
                
                elif self._state is EXECUTING:
                    executing_eff = self._execution_stack[0]
                    result = executing_eff.check()
                    self._effectlist = [
                        eff
                        for gameobject in self.gameobjects()
                        for eff in gameobject.effects
                        ]
                    self._execution_stack = [
                        eff for eff in self._execution_stack
                        if eff in self._effectlist
                        ]
                    if result is DONE:
                        self._execution_stack.remove(executing_eff)
                    self._state = SEARCHING
                    continue

                # empty stack; check turn end
                if self.get_total_power(self.current_player) > self.get_total_power(self.opponent()):
                    break

                # Idle
                if self.choicelist:
                    choicedict = {
                        (choice.click, choice.drop) : choice
                        for choice in self.choicelist
                    }
                    self._state = SELECT

                    message = 'Choose!'
                    drag = None
                    while drag not in choicedict:
                        drag = yield message
                        message = 'Invalid Choice!'

                    chosen = choicedict[drag].effect
                    chosen.check()
                    self._execution_stack.append(chosen)
                else:
                    return End()
            #back to the loop
