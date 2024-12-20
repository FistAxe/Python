from typing import Callable, Literal
LOSE = 'lose'

class Card:
    def __init__(self, name='default card', *effects):
        self.name = name
        self.effects: list[Effect] = []
        self.on_face = False
        if effects != ():
            for effect in effects:
                self.effects.append(effect)
        self._location: Pack = None

    @property
    def location(self):
        return self._location
    
    @location.setter
    def location(self, new_location):
        if self._location != new_location:
            self._location = new_location

    def on_top(self):
        if self.location.cards[-1] == self:
            return True
        else:
            return False

    def is_revealed(self):
        if not self.on_face:
            return False
        else:
            if isinstance(self.location, Zone):
                if self.on_top():
                    return 'full'
                else:
                    return 'half'
            elif isinstance(self.location, Graveyard) and self.on_top():
                return 'full'
            else:
                raise Exception('Cannot define if card is revealed!')

class Creature(Card):
    def __init__(self, name='default creature', power=1, speed=None, *effects):
        super().__init__(name)
        self.power = power
        self.speed = speed

class Spell(Card):
    def __init__(self, name='default spell', speed=1):
        super().__init__(name)
        self.speed = speed

class Artifact(Card):
    def __init__(self, name='default artifact', speed=None):
        super().__init__(name)
        self.speed = speed

class Effect:
    def __init__(self, halfboard:'HalfBoard', bind_to=None):
        if halfboard:
            self.halfboard = halfboard
            self.board = self.halfboard.board
        self.bind_to = bind_to
        self.effectblocks: list[tuple[EffectBlock, int|None, int|None]] = []
        '''How to Use: (EffectBlock, next index if True, next index if False)'''

class EffectBlock:
    def __init__(self, effect:Effect):
        self.effect = effect

    @property
    def index(self):
        for i, eb in enumerate([tup[0] for tup in self.effect.effectblocks]):
            if eb == self:
                return i
        # If there's no matching index:
        raise Exception('Effectblock not included in Effect!')

class Condition(EffectBlock):
    def __init__(self, effect:Effect, check:Callable[..., bool|int]=None):
        super().__init__(effect)
        self.activated: bool = True
        if check:
            self.check = check

    def check(self) -> bool|int :
        return False

    def activation_check(self):
        return self.activated

class Restriction(EffectBlock):
    def verify(self, act:'EffectBlock') -> bool:
        return True

class Choice(EffectBlock):
    def __init__(self, effect: Effect):
        super().__init__(effect)
        self.key = None

    def choose(self):
        return self.effect.effectblocks[self.index][1]


class Action(EffectBlock):
    def process(self) -> bool|str:
        return True
    
class Pack():
    class _IsEmptyCondition(Condition):
        def __init__(self, pack:'Pack'):
            self.pack = pack
            self.num: int|None = None

        def __call__(self, effect, num=None):
            super().__init__(effect)
            if num:
                self.num = num
            return self

        def check(self):
            if self.num:
                return self.pack.is_empty(self.num)
            else:
                return self.pack.is_empty()

    def __init__(self, halfboard:'HalfBoard'):
        self.cards: list[Card] = []
        self.halfboard = halfboard
        self.effects: list[Effect] = []
        self.IsEmptyCondition = self._IsEmptyCondition(self)

    def is_empty(self, num=None):
        if num:
            return True if len(self.cards) >= num else False
        else:
            return True if len(self.cards) == 0 else False

class Zone(Pack):
    def __init__(self, halfboard:'HalfBoard'):
        super().__init__(halfboard)
        self.name = 'error: not specific zone'

    def is_empty(self, board):
        if super().is_empty(board):
            return self.collapse()

    def collapse(self):
        self.cards.clear()

class Deck(Pack):
    class _DrawAction(Action):
        def __init__(self, deck:'Deck'):
            self.deck = deck

        def __call__(self, effect:'Effect', num:int=1):
            super().__init__(effect)
            self.num = num
            return self

        def process(self):
            for _ in range(self.num):
                self.deck.halfboard.hand.cards.append(self.deck.cards.pop())
                self.deck.halfboard.hand.cards[-1].location = self.deck.halfboard.hand
            return True
    
    class _BaseDrawAction(_DrawAction):
        def process(self):
            self.deck.drawed = True
            super().process()

    class BaseDrawEffect(Effect):
        class BaseDrawCondition(Condition):
            def check(self):
                return bool(self.effect.halfboard.board.current_player == self.effect.halfboard) * \
                       bool(not self.effect.deck.drawed)
            
        class BaseDrawChoice(Choice):
            def __init__(self, effect: 'Deck.BaseDrawEffect'):
                super().__init__(effect)
                self.key = self.effect.deck

            def choose(self):
                if self.effect.halfboard.board.holding_from == self.effect.deck:
                    super().choose()

        def __init__(self, halfboard: 'HalfBoard', deck: 'Deck'):
            super().__init__(halfboard, None)
            self.deck = deck
            self.drawed = False
            self.effectblocks = [
                (self.BaseDrawCondition(self), 1),
                (self.deck.IsEmptyCondition(self), 4, 2),
                (self.BaseDrawChoice(self), 3),
                (self.deck.BaseDrawAction(self, 1),),
                (self.deck.halfboard.LoseAction(self),)
            ]

    def __init__(self, halfboard):
        super().__init__(halfboard)
        self.IsEmptyCondition = self._IsEmptyCondition(self)
        self.DrawAction = self._DrawAction(self)
        self.BaseDrawAction = self._BaseDrawAction(self)
        self.basedraweffect = self.BaseDrawEffect(self.halfboard, self)
        self.drawed = False
        self.effects.append(self.basedraweffect)

class Graveyard(Pack):
    def __init__(self, halfboard):
        super().__init__(halfboard)

class Hand(Pack):
    def __init__(self, halfboard:'HalfBoard'):
        super().__init__(halfboard)
        self.name = f"{self.halfboard.name}'s hand"

class MainZone(Zone):
    def __init__(self, halfboard:'HalfBoard'):
        super().__init__(halfboard)
        self.name = f"{self.halfboard.name}'s Main Zone"

    def collapse(self):
        super().collapse()
        return self.halfboard.board.lose(self.halfboard)

class SubZone(Zone):
    def __init__(self, halfboard):
        super().__init__(halfboard)
        self.trigger = self.is_empty

    def rename(self):
        self.index = self.halfboard.row.subzones.index(self)
        self.name = f"{self.halfboard.name}'s Sub Zone {self.index}"

    def collapse(self):
        super().collapse()
        self.halfboard.row.remove(self)

class Row:
    def __init__(self, halfboard:'HalfBoard'):
        self.halfboard = halfboard
        self.name = f"{self.halfboard.name}'s Row"
        self.subzones: list[SubZone] = []

    def rename(self):
        for subzone in self.subzones:
            subzone.index = self.subzones.index(subzone)
            subzone.name = f"{self.halfboard.name}'s Sub Zone {subzone.index}"

    def insert(self, index):
        self.subzones.insert(index, SubZone(self.halfboard))
        self.rename()

    def remove(self, subzone:SubZone):
        self.subzones.remove(subzone)
        self.rename()

class HalfBoard:
    _board: 'Board' = None

    class LoseAction(Action):
        pass

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
        return self._board

    def get_suborder(self):
        return len(self.row.subzones)

class Attack(Action):
    pass

class Activate(Action):
    pass

class Let(Action):
    def __init__(self, board:'Board', halfboard:HalfBoard, card:Card, zone:Zone, came_from:Zone|Hand|Graveyard):
        super().__init__(board, halfboard)
        self.card = card
        self.zone = zone
        self.came_from = came_from

    def declare(self):
        if self.board == self.came_from:
            self.check = False
        ans = super().declare()
        if not ans:
            self.board.drop_holding()
        return ans

    def process(self):
        self.zone.cards.append(self.card)
        self.board.drop_holding(True)
        result = super().process()
        if isinstance(self.zone, MainZone):
            self.board.current_player = self.board.opponent()
        return result

class Deploy(Let):
    def __init__(self, board:'Board', halfboard:HalfBoard, card:Card, subzone_num:int):
        super().__init__(board, halfboard)
        self.card = card
        self.new_index = subzone_num - 1

    def declare(self):
        if len(self.halfboard.row.subzones) > 4:
            self.check = False
        ans = super().declare()
        # No Process
        if ans == False:
            self.board.drop_holding()   # drop
            return False
        # Process -> drop ocurred while processing
        else:
            return ans
    
    def process(self):
        self.halfboard.row.insert(self.new_index)
        self.halfboard.row.subzones[self.new_index].cards.append(self.board.holding)
        self.halfboard.row.subzones[self.new_index].cards[-1].location = self.halfboard.row.subzones[self.new_index]
        self.board.drop_holding(True)
        return super().process()

class Board:
    class InitialSetting(Effect):
        def __init__(self, board:'Board'):
            super().__init__(None, board)
            self.effectblocks = [
                (board.player1.deck.DrawAction(self, 5),),
                (board.player2.deck.DrawAction(self, 5),)
            ]

    def __init__(self, player1:HalfBoard, player2:HalfBoard):
        self.player1 = player1
        self.player2 = player2
        self.players = [player1, player2]
        self.loser = False
        self.current_player: HalfBoard = player1
        self.turn = [0, 0]
        self.state = 'Init'
        self.action_stack: list[Action] = []
        self.restrictions: list[Restriction] = []

        for player in self.players:
            player._board = self

        self.holding = None
        self.holding_from = None
        self.drawing = False
        self.gamecomponents: list[HalfBoard|Pack|Card] = []

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
        self.gamecomponents = []
        for player in self.players:
            self.gamecomponents.append(player)
            self.gamecomponents.append(player.deck)
            self.gamecomponents.append(player.hand)
            self.gamecomponents.append(player.graveyard)
            if len(player.graveyard.cards) > 0:
                self.gamecomponents.append(player.graveyard.cards[0])
            for zone in player.zones:
                self.gamecomponents.append(zone)
                for card in zone.cards:
                    self.gamecomponents.append(card)
        return self.gamecomponents

    def get_processing_order(self):
        order: list[Card|Pack|Board|HalfBoard] = []
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
            if player.main_zone.cards != []:
                order.append(player.main_zone.cards[0])
            for zone in player.row.subzones:
                order.append(zone.cards[0])
            if player.main_zone.cards != []:
                order.append(player.graveyard.cards[0])
        return order

    def process_action(self, action:Action):
        return action.process()

    def initial_setting(self):
        a = self.InitialSetting(self)
        for eb in a.effectblocks:
            eb[0].process()

    def interpret(self, typ:Literal['click', 'drop'], keys:list[Pack|Card|str], index:int|None=None):
        # Key selection
        key = None
        for k in keys:
            if isinstance(k, str) or isinstance(k, Deck) or isinstance(k, Graveyard) or isinstance(k, Zone):
                key = k
                break
            # If there is only Hand and card, return card.
            elif isinstance(k, Card):
                key = k
            elif isinstance(k, Board) or isinstance(k, HalfBoard) or isinstance(k, Row):
                pass
            else:
                raise Exception('Something weird in keys!')
        
        if typ == 'click':
            if isinstance(key, Card):
                self.holding = key
                self.holding_from = self.holding.location
            elif isinstance(key, Zone) or isinstance(key, Graveyard):
                self.holding_from = key
                self.holding = self.holding_from.cards[-1]
            elif isinstance(key, Deck):
                self.holding_from = key
                self.holding = None
            return True
        
        elif typ == 'drop':
            for choice in self.current_player.available_choices:
                if choice.key == key:
                    return choice
        else:
            raise Exception('Not click nor drop!')
        
        return False

    def drop_holding(self, is_moved:bool=False):
        if is_moved:
            self.holding_from.cards.remove(self.holding)
        self.holding = None
        self.holding_from = None

    def play(self):
        for i in range(10):
            new_card = Card(str(i))
            new_card.location = self.player1.deck
            self.player1.deck.cards.append(new_card)
            new_enm_card = Card(str('enm'+f'{ i}'))
            new_enm_card.location = self.player2.deck
            self.player2.deck.cards.append(new_enm_card)

        self.initial_setting()
        self.player2.main_zone.cards.append(Card('main card'))

        while not self.loser:
            print('start loop')

            self.action_stack = []
            self.current_player.available_choices = []

            # While there are any actions
            calculating = True
            while calculating:
                for gamecomponent in self.refresh_gamecomponents():
                    for effect in gamecomponent.effects:
                        tup = effect.effectblocks[0]
                        while tup:
                            # Condition.check() adds restriction into the list.
                            if isinstance(tup[0], Condition):
                                if tup[0].check():
                                    index = tup[1]
                                elif len(tup) > 2 and tup[2]:
                                    index = tup[2]
                                else:
                                    tup = None
                                    break
                                tup = effect.effectblocks[index]
                            else:
                                if isinstance(tup[0], Restriction):
                                    self.restrictions.append(tup[0])
                                # Ignore Effects that need Choice
                                elif isinstance(tup[0], Choice):
                                    self.current_player.available_choices.append(tup[0])
                                # Finally, add Action.
                                elif isinstance(tup[0], Action):
                                    self.action_stack.append(tup[0])
                                tup = None

                for action in self.action_stack:
                    for restriction in self.restrictions:
                        if restriction.verify(action) == False:
                            self.action_stack.remove(action)

                if self.action_stack == []:
                    calculating = False
                    break
                else:
                    result = self.process_action(self.action_stack[-1])
                    if result == 'end':
                        yield 'end!'
                        break
                    self.action_stack.pop()
                # Go to the beginning, and make action list again.
            
            # When no item in actionlist:
            for choice in self.current_player.available_choices:
                for restriction in self.restrictions:
                    if restriction.verify(choice) == False:
                        self.current_player.available_choices.remove(choice)
            #yield True

            # From here, no actions. Player choose what to do.
            args: list[str, list, int|None] = yield
            print('got message')
            if args != None:
                # If interpreting was not successful, send error message.
                choice = self.interpret(*args)
                if choice == False:
                    self.drop_holding()
                else:
                    next_effect_index = None
                    if isinstance(choice, Choice):
                        next_effect_index = choice.choose()
                    if next_effect_index:
                        self.action_stack.append(choice.effect.effectblocks[next_effect_index][0])

            print('end loop')

    def lose(self, player:HalfBoard):
        self.loser = player
        print(f'game end! {self.opponent(self.loser)} survives.')
        return 'end'


#input player 1, 2 {name, deck, etc}
#player1 = HalfBoard('Player 1')
#player2 = HalfBoard('Player 2')
#game = Board(player1, player2)

#game.play()