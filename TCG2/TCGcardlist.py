import TCG

class Bear(TCG.Creature):
    def __init__(self, owner: TCG.HalfBoard):
        super().__init__(
            owner,
            name = 'Bear',
            color = 'Y',
            power = 3,
            description = 'Just a bear.',
            image = './images/Bear.png'
            )
        
class FireBall(TCG.Spell):
    def __init__(self, owner: TCG.HalfBoard):
        super().__init__(
            owner,
            name = 'Fire Ball',
            color = 'R',
            image = './images/Fireball.png',
            description= 'asdf'
            )
        
class Goblet(TCG.Spell):
    def __init__(self, owner: TCG.HalfBoard):
        super().__init__(
            owner,
            name = 'Goblet',
            color = 'B',
            description = 'A goblet.',
            image = './images/Goblet.png'
        )

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

    def __init__(self, owner: TCG.HalfBoard):
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