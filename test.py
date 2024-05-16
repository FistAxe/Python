from rich import print
from rich.layout import Layout
from rich.panel import Panel
from rich.console import group

@group()
def get_panels():
    yield Panel("Hello", style="on blue")
    yield Panel("World", style="on red")

layout = Layout(get_panels())

print(layout)