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