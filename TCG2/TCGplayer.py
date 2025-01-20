import TCG
import TCGcardlist as cl

player1 = TCG.HalfBoard('Player 1')
player1.cardlist = [
    cl.Bear,
    cl.Bear,
    cl.CursedDefeatButton,
    cl.CursedDefeatButton,
    cl.CursedDefeatButton,
    cl.FireBall,
    cl.FireBall,
    cl.Goblet,
    cl.Goblet
]

player2 = TCG.HalfBoard('Player 2')
player2.cardlist = [
    cl.Bear,
    cl.Bear,
    cl.Bear,
    cl.Bear,
    cl.FireBall,
    cl.FireBall,
    cl.FireBall,
    cl.Goblet,
    cl.Goblet,
    cl.Goblet
]