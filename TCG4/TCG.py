from typing import Literal

class PlayerInfo:
    def __init__(self, name, cardlist:list[type[Card]]):
        self.name = name
        self.cardlist = cardlist

class Effect:
    def __init__(self, source:GameObject) -> None:
        self._source = source

    @property
    def source(self):
        return self._source
    
    def get_choice(self):
        return Choice()
    
    def eval(self):
        pass

    def execute(self):
        pass

class Choice:
    pass

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
        self._rules = []
        self._player1 = Player(self, player1info)
        self._player2 = Player(self, player2info)
        self._current_player: Player = self._player1
        self._effectlist: list[Effect] = []
        self._event_que = []

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
    def event_que(self):
        return tuple(self._event_que)

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

    def get_choices(self):
        choices: list[Choice] = []
        self._update()
        for eff in self.effectlist:
            choice = eff.get_choice()
            if choice:
                choices.append(choice)
        return choices

    def _update(self):
        self._effectlist = []
        for gameobject in self.gameobjects():
            for effect in gameobject.effects:
                self._effectlist.append(effect)

    def _run(self):
        chosen: Choice|None = None
        paused = None
        self._event_que = []

        #turn start
        while True:
            while True:
                chosen = None
                for rule in self._rules:
                    if rule:
                        #do something
                        continue
                if self._event_que:
                    paused = self._event_que[0]
                    self._update()
                    for effect in self._effectlist:
                        if effect.eval():
                            self._event_que.append(effect)
                    if paused is self._event_que[0]:
                        paused.execute()
                    paused = None
                    continue
                if self.get_total_power(self.current_player) > self.get_total_power(self.opponent()):
                    break
                #Idle; gather choices
                choices = self.get_choices()
                if choices:
                    chosen = yield choices
                    self._event_que.append(chosen)
                else:
                    return End()
            #back to the loop

    def IO(self):
        command: Choice|Literal['Cancel']|None = None
        ui_input: GameObject|Literal['Cancel']|None

        game = self._run()  # Start the game engine generator
        yield 'Game Engine Start'
        
        while True:
            # String Ignorance Loop
            while True:
                ui_output = game.send(command)
                if isinstance(ui_output, str):
                    yield ui_output
                    command = None
                elif isinstance(ui_output, End):
                    return ui_output
                # Now list given
                else:
                    choices = ui_output
                    break

            # Command Loop
            while not command:
                selected_source: GameObject|None = None
                selected_target: GameObject|None = None

                # Drag Loop
                ui_input = yield choices

                # If Canceled on Source Loop, back to the initial Choices
                if isinstance(ui_input, GameObject) and ui_input in {c['source'] for c in choices}:
                    selected_source = ui_input
                elif ui_input == 'Cancel':
                    command = CANCEL
                    print(f"Selected Choice: 'CANCEL'")

                if not selected_source:
                    print("Got None in the first IO!")
                    continue
                    
                # Drop Loop
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

