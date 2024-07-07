from rich import print
from rich.panel import Panel
from rich.text import Text
from rich.console import Group
from rich.align import Align
panel = Panel(Group(Align(Text('Wow', end=''), align='left'), Text("Hello", justify="right")))
print(panel)