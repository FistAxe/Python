LOSE = 'lose'

class Card:
    effects: list['Effect']
    def __init__(self, name='default card'):
        self.name = name

class Creature(Card):
    def __init__(self, name='default creature'):
        super().__init__(name)

class Spell(Card):
    def __init__(self, name='default spell'):
        super().__init__(name)

class Artifact(Card):
    def __init__(self, name='default artifact'):
        super().__init__(name)

class Effect():
    condition: 'Condition'
    pass

class Zone:
    def __init__(self, halfboard:'HalfBoard'):
        self.name = 'error: not specific zone'
        self.cards: list[Card] = []
        self.halfboard = halfboard

class Deck:
    def __init__(self, halfboard):
        self.cards: list[Card] = []
        self.halfboard = halfboard

    def pop(self, num):
        try:
            pops = []
            for _ in num:
                pops += self.cards.pop()
            return pops
        except IndexError:
            return 'Deck ran out!'

class Graveyard:
    def __init__(self, halfboard):
        self.cards: list[Card] = []
        self.halfboard = halfboard

class MainZone(Zone):
    def __init__(self, halfboard:'HalfBoard'):
        super().__init__(halfboard)
        self.name = f"{self.halfboard.name}'s Main Zone"

class SubZone(Zone):
    def __init__(self, halfboard):
        super().__init__(halfboard)
        self.suborder = self.halfboard.get_suborder()
        self.name = f"{self.halfboard.name}'s Main Zone {self.suborder}"

class Row:
    def __init__(self, halfboard:'HalfBoard'):
        self.halfboard = halfboard
        self.name = f"{self.halfboard.name}'s Row"
        self.subzones: list[SubZone] = []

class HalfBoard:
    def __init__(self, player_name:str):
        self.name = player_name
        self.deck = Deck(self)
        self.graveyard = Graveyard(self)
        self.main_zone = MainZone(self)
        self.row = Row(self)

    def get_suborder(self):
        return len(self.row.subzones)

    def draw(self, num):
        return Draw(self, num)

class Action:
    def __init__(self, name, board:'Board'):
        self.name = name
        self.board = board

    def declare(self):
        self.board.action_que.append(self)

    def process(self):
        pass

class Draw(Action):
    def __init__(self, halfboard:HalfBoard, num):
        self.halfboard = halfboard
        self.num = num

    def declare(self):
        super().declare()

    def process(self):
        self.drawn_cards = self.halfboard.deck.pop(self.num)
        super().process()

class Attack(Action):
    pass

class Activate(Action):
    pass

class Condition:
    def __init__(self):
        pass

    def check(self, board):
        return 'Able'

class Board:
    def __init__(self, player1:HalfBoard, player2:HalfBoard):
        self.player1 = player1
        self.player2 = player2
        self.players = [player1, player2]
        self.loser = False
        self.current_turn: HalfBoard = None
        self.turn = [0, 0]
        self.conditions: list[Condition] = []
        self.action_que: list[Action] = []
        self.state = 'Init'

    def opponent(self, player:HalfBoard|None) -> HalfBoard:
        if player == self.player1:
            return self.player2
        elif player == self.player2:
            return self.player1
        elif player == None:
            return self.player1
        else:
            raise ValueError

    def get_processing_order(self):
        cards: list[Card] = []
        for player in [self.opponent(self.current_turn), self.current_turn]:
            cards.append(player.main_zone.cards[0])
            for zone in player.row.subzones:
                cards.append(zone.cards[0])
            cards.append(player.graveyard.cards[0])
        return cards

    def inspector(self):
        for card in self.get_processing_order():
            for effect in card.effects:
                result = effect.condition.check(self)
                if result == LOSE:
                    self.loser = effect.condition.loser
                    return 0

    def initial_setting(self):
        for player in self.players:
            player.draw(5)
            self.inspector()

    def get_action(self, key):
        pass

    def play(self):
        self.initial_setting()
        while not self.loser:
            while self.state not in ('declaring', 'processing'):
                try:
                    self.action_que.pop().process()
                except IndexError:
                    self.choose_action(self.current_turn)
            self.inspector()
            yield 'running'
            result = yield
            if result[2] != []:
                for key in result[2]:
                    self.get_action(key)
            if result[1] != []:
                for key in result[1]:
                    self.get_action(key)
            if result[0] != []:
                for key in result[0]:
                    self.get_action(key)

        print(f'game end! {self.opponent(self.loser)} survives.')


#input player 1, 2 {name, deck, etc}
player1 = HalfBoard('Player 1')
player2 = HalfBoard('Player 2')
game = Board(player1, player2)

game.play()