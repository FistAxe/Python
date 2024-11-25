class Zone:
    def __init__(self):
        self.cards = []

class Deck:
    def __init__(self):
        self.cards = []

class Graveyard:
    cards = []

class Hand:
    cards = []

class HalfBoard:
    def __init__(self, *args):
        self.deck = Deck()
        self.mainzone = Zone()
        self.row: list[Zone] = []
        self.graveyard = Graveyard()
        self.hand = Hand()

def interpret(*args):
    place = ''
    card = ''
    if len(args) == 0:
        return None
    else:
        place = args[0]
        if len(args) > 1:
            card = args[1]
            if len(args) > 2:
                if place == 'temp zone':
                    new_subzone_index = args[2]
                    return place, card, new_subzone_index


class Board:
    def __init__(self, p1:HalfBoard, p2:HalfBoard):
        self.player1 = p1
        self.player2 = p2

    def play(self):
        for i in range(10):
            self.player1.deck.cards.append(i)

        self.player1.row.append(Zone())
        self.player1.mainzone.cards.append('main card')
        self.player1.row[0].cards.append('sub card')
        while True:
            #yield True
            print('start loop')
            args: list[str, ] = yield
            print('got message')
            if args != None and len(args) > 2 and args[0] == 'temp zone':
                if len(self.player1.row) > 4:
                    yield 'too many sub zones!'
                else:
                    self.player1.row.insert(args[2] - 1, Zone())
                    self.player1.row[args[2] - 1].cards.append('1')
                yield True
            else:
                yield 'a'
            print('end loop')
