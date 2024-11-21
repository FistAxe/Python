LOSE = 'lose'

class Card:
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

class Zone:
    def __init__(self, halfboard:'HalfBoard'):
        self.name = 'error: not specific zone'
        self.cards = []
        self.halfboard = halfboard

class Deck:
    def __init__(self, halfboard):
        self.cards = []
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
        self.cards = []
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
        self.subzones = []

class HalfBoard:
    def __init__(self, player_name:str):
        self.name = player_name
        self.deck = Deck()
        self.graveyard = Graveyard()
        self.main_zone = MainZone()
        self.row = Row()

    def draw(self, num):
        return Draw(self, num)

class Action:
    def __init__(self, name):
        self.name = name

    def declare(self):
        pass

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

class Board:
    def __init__(self, player1:HalfBoard, player2:HalfBoard):
        self.player1 = player1
        self.player2 = player2
        self.players = [player1, player2]
        self.loser = False
        self.current_turn = None
        self.turn = [0, 0]
        self.conditions = []
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

    def inspector(self):
        for condition in self.conditions:
            result = condition.check(self)
            if result == LOSE:
                self.loser = condition.loser

    def initial_setting(self):
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

        print(f'game end! {self.opponent(self.loser)} survives.')


#input player 1, 2 {name, deck, etc}
player1 = HalfBoard()
player2 = HalfBoard()
game = Board(player1, player2)

game.play()