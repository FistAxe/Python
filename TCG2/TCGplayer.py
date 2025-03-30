import TCG
import TCGcardlist as cl

player1 = TCG.HalfBoard('Player 1')
player1.deck._cards = [
    cl.Bear(player1),
    cl.Bear(player1),
    cl.FireBall(player1),
    cl.FireBall(player1),
    cl.Goblet(player1),
    cl.Goblet(player1)
]

player2 = TCG.HalfBoard('Player 2')
player2.deck._cards = [
    cl.Bear(player2),
    cl.Bear(player2),
    cl.Bear(player2),
    cl.Bear(player2),
    cl.FireBall(player2),
    cl.FireBall(player2),
    cl.FireBall(player2),
    cl.Goblet(player2),
    cl.Goblet(player2),
    cl.Goblet(player2)
]