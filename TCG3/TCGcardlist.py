import sys
import os
root_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(root_dir)
import TCG

class Bear(TCG.Creature):
    _name = 'Bear'
    _color = 'Y'
    _power = 3
    _description = 'Just a bear.'
    _image = os.path.join(root_dir, 'images', 'Bear.png')

class FireBall(TCG.Spell):
    _name = 'Fire Ball'
    _color = 'R'
    _image = os.path.join(root_dir, 'images', 'Fireball.png')
    _description= 'asdf'

class Goblet(TCG.Spell):
    _name = 'Goblet'
    _color = 'B'
    _description = 'A goblet.'
    _image = os.path.join(root_dir, 'images', 'Goblet.png')

'''
class CursedDefeatButton(TCG.Spell):
    class ButtonPressedEffect(TCG.Effect):
        bind_to: 'CursedDefeatButton'

        class ButtonPressChoice(TCG.Choice):
            def match(self, key: TCG.GameComponent | str | TCG.Choice | None, index: int | None) -> bool:
                return super().match(key, index) and self.clicked()

        def _execute(self, in_event: TCG.Choice|TCG.Action| None):
            if self.chosen(in_event):
                return self.bind_to.owner.get_loseaction(self)
            elif self.bind_to.active == 'active' and not in_event and self.bind_to.is_for_current_player():
                return self.ButtonPressChoice(self)

    def __init__(self, owner: TCG.Player):
        super().__init__(
            owner,
            name = 'Cursed Defeat Button',
            color = None,
            description = 'No one could resist the urge.',
            image = None
        )
        self._effects.append(self.ButtonPressedEffect(self))''
        ''
'''