import TCG

class Bear(TCG.Creature):
    def __init__(self, owner: TCG.HalfBoard):
        super().__init__(
            owner,
            name = 'Bear',
            color = 'Y',
            power = 3,
            discription = 'Just a bear.',
            image = './images/Bear.png'
            )
        
class FireBall(TCG.Spell):
    def __init__(self, owner: TCG.HalfBoard):
        super().__init__(
            owner,
            name = 'Fire Ball',
            color = 'R',
            speed = 1,
            image = './images/Fireball.png'
            )
        
class Goblet(TCG.Artifact):
    def __init__(self, owner: TCG.HalfBoard):
        super().__init__(
            owner,
            name = 'Goblet',
            color = 'B',
            discription = 'A goblet.',
            image = './images/Goblet.png'
        )

class CursedDefeatButton(TCG.Artifact):
    class ButtonPressedEffect(TCG.Effect):
        bind_to: 'CursedDefeatButton'
        class ButtonPressedCondition(TCG.Condition):
            def check(self, in_action):
                return super().check(in_action) and \
                       not in_action and \
                       self.effect.bind_to.is_for_current_player() and \
                       not self.effect.is_reserved()
        class ButtonPressChoice(TCG.Choice):
            pass
        def __init__(self, bind_to: 'CursedDefeatButton'):
            super().__init__(bind_to)
            self.effectblocks = [
                TCG.EffChain(self.ButtonPressedCondition(self), 1),
                TCG.EffChain(self.ButtonPressChoice(self, has_button=True, image='default'), 2),
                TCG.EffChain(self.bind_to.owner.get_loseaction(self))
            ]
    def __init__(self, owner: TCG.HalfBoard):
        super().__init__(
            owner,
            name = 'Cursed Defeat Button',
            color = None,
            discription = 'No one could resist the urge.',
            image = None
        )
        self._effects.append(self.ButtonPressedEffect(self))