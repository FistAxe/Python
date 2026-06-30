from enum import Enum, auto
from dataclasses import dataclass
from typing import Literal, Generator

class Keywords(Enum):
    CANCEL = auto()
    """A cancel message."""
    IDLE = auto()
    SELECT = auto()
    SEARCHING = auto()
    EXECUTING = auto()
    INIT = auto()

    INACTIVE = auto()
    READY = auto()
    ACTIVE = auto()
    DONE = auto()

CANCEL = Keywords.CANCEL
SELECT = Keywords.SELECT
SEARCHING = Keywords.SEARCHING
EXECUTING = Keywords.EXECUTING
INIT = Keywords.INIT
IDLE = Keywords.IDLE
INACTIVE = Keywords.INACTIVE
READY = Keywords.READY
ACTIVE = Keywords.ACTIVE
DONE = Keywords.DONE

class PlayerInfo:
    def __init__(self, name, cardlist:list[type[Card]]):
        self.name = name
        self.cardlist = cardlist

class Effect:
    def __init__(self, source:GameObject) -> None:
        self._source = source
        self._stage: Keywords|None = None

    @property
    def source(self):
        return self._source
    
    @property
    def stage(self):
        return self._stage
    
    def check(self) -> list[Choice]|Keywords|None:
        return self.stage

class Execution:
    def __init__(self, effect:Effect) -> None:
        self._effect = effect
    
    @property
    def effect(self):
        return self._effect

@dataclass
class Choice:
    effect: Effect
    target: GameObject

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

    def _search_chain_effect(self):
        for eff in self._effectlist:
            if eff not in self._execution_stack and eff.check() is ACTIVE:
                self._execution_stack.append(eff)

    def _run(self) -> Generator[str|Keywords, Choice|None, End]:
        chosen: Choice|None = None
        self._execution_stack = []

        #turn start
        while True:
            self._current_player = self.opponent()
            while True:
                self._state = SEARCHING
                chosen = None
                if self._execution_stack:
                    executing_eff = self._execution_stack[0]
                    self._search_chain_effect()

                    if executing_eff is not self._execution_stack[0]:
                        continue
                    
                    self._state = EXECUTING
                    result = executing_eff.check()
                    self._effectlist = [
                        effect
                        for gameobject in self.gameobjects()
                        for effect in gameobject.effects
                    ]
                    for i in range(len(self._execution_stack)-1, -1, -1):
                        if self._execution_stack[i] not in self._effectlist:
                            self._execution_stack.pop(i)
                    if result is DONE:
                        self._execution_stack.remove(executing_eff)
                    elif isinstance(result, list):
                        self._state = SELECT
                        chosen = None
                        self._choicelist = result
                        while not chosen:
                            chosen = yield SELECT
                    continue

                # empty stack; check turn end
                if self.get_total_power(self.current_player) > self.get_total_power(self.opponent()):
                    break

                # Idle; gather choices
                self._choicelist = []
                for eff in self._effectlist:
                    choice = eff.check()
                    if isinstance(choice, Choice):
                        self._choicelist.append(choice)
                
                if self._choicelist:
                    self._state = SELECT
                    while not isinstance(chosen, Choice):
                        chosen = yield SELECT
                    self._execution_stack.append(chosen.effect)
                else:
                    return End()
            #back to the loop

    def IO(self):
        engine_output: Keywords|str|End|None = None
        engine_input: Choice|Keywords|None = None
        ui_message: GameObject|Keywords|None = None

        engine = self._run()  # Start the game engine generator
        next(engine)
        yield 'Game Engine Start'
        
        while True:
            # Log Loop
            try:
                engine_output = engine.send(engine_input)
            except StopIteration as e:
                end: End = e.value
                return end
            
            if isinstance(engine_output, str):
                yield engine_output
                ui_message = None
                continue

            # Command Loop
            while not ui_message:
                ui_message = yield engine_output

            if isinstance(ui_message, GameObject):
                ui_message = None
