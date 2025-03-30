from typing import Literal

class GameComponent:
    _name = 'GameComponent'
    
    @property
    def name(self):
        return self._name

class Effect:
    pass

class Choice:
    pass

class Button:
    def __init__(self, image) -> None:
        self.image = image

class Card(GameComponent):
    on_face = False
    def __init__(self, owner, name, color:Literal['R', 'Y', 'B']|None, power=None, image=None, description=None) -> None:
        super().__init__()
        self.owner = owner
        self._name = name
        self._color = color
        self._image = image
        self._power = power
        self._description = description
        self.on_face = False
        self.time: Literal[1, 2, 3, 4]|None = None

    @property
    def name(self):
        return self._name if self.on_face else None
    
    @property
    def color(self):
        return self._color if self.on_face else None

    @property
    def power(self):
        return self._power if self.on_face else None

    @property
    def image(self):
        return self._image if self.on_face else None
    
    @property
    def description(self):
        return self._description if self.on_face else None

class Creature(Card):
    pass

class Spell(Card):
    pass

class Pack(GameComponent):
    def __init__(self) -> None:
        super().__init__()
        self._cards = []

    @property
    def length(self):
        return len(self._cards)

class Zone(GameComponent):
    class Let(Effect):
        pass

    def __init__(self) -> None:
        super().__init__()
        self.card = None

    @property
    def power(self):
        return self.card.power if self.card else 0

class MainZone(Zone):
    class Let(Effect):
        pass
    pass

class SubZone(Zone):
    class Let(Effect):
        pass
    pass

class Deck(Pack):
    pass

class Graveyard(Pack):
    pass

class Hand(Pack):
    def __init__(self) -> None:
        super().__init__()

class HalfBoard(GameComponent):
    def __init__(self, name) -> None:
        self.deck = Deck()
        self.graveyard = Graveyard()
        self.hand = Hand()
        self.mainzones = [
            MainZone(),
            MainZone(),
            MainZone()
        ]
        self.subzones = [
            SubZone(),
            SubZone(),
            SubZone()
        ]
        self.zones = self.mainzones + self.subzones

    @property
    def total_power(self):
        return sum([zone.power for zone in self.zones])

class Board(GameComponent):
    def __init__(self, player1:HalfBoard, player2:HalfBoard) -> None:
        super().__init__()
        self.player1 = player1
        self.player2 = player2
        self.current_player = None
        self.holding = None
        self.loser = None

        self.active_choices = []

    def opponent(self, player:HalfBoard|None=None):
        if player:
            return self.player1 if player is self.player2 else self.player2
        else:
            return self.player2 if self.current_player is self.player1 else self.player1

    def play(self):
        yield 'end!'