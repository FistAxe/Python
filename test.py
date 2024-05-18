import random
import time

from rich.live import Live
from rich.table import Table
from rich.console import Group
from rich.prompt import Prompt
from rich.layout import Layout

answer : str = "init"

def promptgen():
    return Prompt.ask("asdf")
prompt = Prompt.ask("press q")

layout = Layout(
    promptgen()
)


with Live(layout in range(40)) as live:
    while 1:
        live.update(layout)
        if answer == 'q':
            break