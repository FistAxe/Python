# Base class for all game components
class GameComponent:
    def __init__(self, name, description):
        self.name = name
        self.description = description

    def __str__(self):
        return f"{self.name}: {self.description}"

# Card class for all card classes
class Card(GameComponent):
    def __init__(self, name, description, mana=False):
        super().__init__(name, description)
        self.mana = mana

# Zone class, base for all zones (Main Zone, Sub Zone, etc.)
class Zone(GameComponent):
    def __init__(self, name, description, has_mana_pool=True):
        super().__init__(name, description)
        self.mana_pool = {'R': 0, 'Y': 0, 'B': 0} if has_mana_pool else False  # Determines if the Zone has a Mana Pool
        self.cards = []

    def let(self, card:Card):
        # Stack action - you let a card into the zone
        self.cards.append(card)
        if type(card.mana) == dict:
            self.mana_pool += card.mana

    def collapse(self):
        # Zone collapses if certain conditions are met
        pass

    def move(self, card, target_zone):
        # Move card between Zones (treated as Letting)
        pass


# Main Zone class, inherits from Zone
class MainZone(Zone):
    def __init__(self):
        super().__init__("Main Zone", "The primary Zone for performing attacks and critical actions.")

    def attack(self, creature):
        # Perform Attack with creature
        pass


# Sub Zone class, inherits from Zone
class SubZone(Zone):
    def __init__(self):
        super().__init__("Sub Zone", "A secondary Zone in the Row, where creatures can't attack but can be targeted.")

    def block(self, creature):
        # Blocking a creature with a Sub Zone creature
        pass


# Base class for all Actions
class Action:
    def __init__(self, name, actor, target=None, speed=0):
        self.name = name
        self.actor = actor
        self.target = target
        self.speed = speed

    def perform(self, board):
        raise NotImplementedError("Each action must implement its perform method.")


# Specific Actions
class DrawAction(Action):
    def __init__(self, actor, num_cards):
        super().__init__("Draw", actor)
        self.num_cards = num_cards

    def perform(self, board):
        drawn_cards = self.actor.draw(self.num_cards)
        print(f"{self.actor} drew {len(drawn_cards)} cards.")
        return drawn_cards


class AttackAction(Action):
    def __init__(self, attacker, target):
        super().__init__("Attack", attacker, target)

    def perform(self, board):
        if self.target:
            print(f"{self.actor.name} attacks {self.target.name}.")
        else:
            print(f"{self.actor.name} attacks directly.")
        # Implement combat logic


class CastAction(Action):
    def __init__(self, spell, target=None, speed=0):
        super().__init__("Cast", spell, target, speed)

    def perform(self, board):
        print(f"{self.actor.name} casts a spell.")
        # Implement spell logic


class ActivateAction(Action):
    def __init__(self, artifact):
        super().__init__("Activate", artifact)

    def perform(self, board):
        print(f"{self.actor.name} activates an artifact.")
        # Implement activation logic

class Creature(Card):
    def __init__(self, name, ATK, SPD):
        super().__init__(name, "A creature card.")
        self.ATK = ATK
        self.SPD = SPD
        self.has_attacked = False

    def attack(self, target, board):
        attack_action = AttackAction(self, target)
        board.queue_action(attack_action)


class Spell(Card):
    def __init__(self, name, effect, speed=0):
        super().__init__(name, "A spell card.")
        self.effect = effect
        self.speed = speed

    def cast(self, target, board):
        cast_action = CastAction(self, target, self.speed)
        board.queue_action(cast_action)


class Artifact(Card):
    def __init__(self, name, effect):
        super().__init__(name, "An artifact card.")
        self.effect = effect

    def activate(self, board):
        activate_action = ActivateAction(self)
        board.queue_action(activate_action)


# Row class for the Sub Zones area
class Row(GameComponent):
    def __init__(self, name, description):
        super().__init__(name, name if description == None else description)
        self.sub_zones = []  # List to hold Sub Zones

    def create_sub_zone(self):
        sub_zone = SubZone()
        self.sub_zones.append(sub_zone)
        return sub_zone


# HalfBoard class to represent each player's half of the board
class HalfBoard(GameComponent):
    def __init__(self, name, description=None):
        super().__init__(name, name if description == None else description)
        self.main_zone = MainZone()
        self.row = Row(name, description)
        self.deck = []  # The player's deck, could be a list of cards
        self.graveyard = list[Card]  # Discarded cards
        self.hand = list[Card]  # The player's hand

    def draw(self, num_cards):
        drawn_cards = [self.deck.pop() for _ in range(min(num_cards, len(self.deck)))]
        print(f"{self.name} drew {[card.name for card in drawn_cards]}.")
        return drawn_cards

    def add_to_graveyard(self, card):
        # Add a card to the graveyard
        self.graveyard.append(card)


# Board class for handling game flow
class Board:
    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        self.action_queue : list[Action] = []

    def queue_action(self, action:Action):
        self.action_queue.append(action)
        print(f"Action queued: {action.name} by {action.actor.name}")

    def process_actions(self):
        # Sort actions by speed and resolve
        self.action_queue.sort(key=lambda action: action.speed, reverse=True)
        for action in self.action_queue:
            action.perform(self)
        self.action_queue.clear()



# Example usage
player1 = HalfBoard("Player 1")
player2 = HalfBoard("Player 2")
board = Board(player1, player2)

# Example cards
creature = Creature("Dragon", 10, 5)
spell = Spell("Fireball", "Deals 5 damage", speed=2)
artifact = Artifact("Ancient Relic", "Increases mana")

# Actions
player1.main_zone.let(creature)
creature.attack(None, board)

player1.main_zone.let(spell)
spell.cast(creature, board)

player1.main_zone.let(artifact)
artifact.activate(board)

# Process actions
board.process_actions()