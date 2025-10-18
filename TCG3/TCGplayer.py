from TCG import Player
import TCGcardlist as cl

player1 = Player('Player 1')
player1._cardlist = [
    cl.Bear(player1),
    cl.Bear(player1),
    cl.FireBall(player1),
    cl.FireBall(player1),
    cl.Goblet(player1),
    cl.Goblet(player1)
]

player2 = Player('Player 2')
player2._cardlist = [
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