from rich import print
from rich.text import Text
from rich.panel import Panel
from rich.console import Group

a = '[on blue]:shield: [on blue]'
b = Text.from_ansi(" \033[D")


print(Panel(Group(a, b), expand=False, padding=(0,1,0,0)))