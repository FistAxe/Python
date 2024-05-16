from rich import print
from rich.layout import Layout
from rich.console import Console
layout = Layout(name="abc")
console = Console()
small_layout = Layout()
small_layout.split_row(
    Layout(),
    Layout()
)

layout.split_row(
    Layout(),
    Layout(name="middle"),
    Layout()
)
layout["middle"].split_column(
    Layout(),
    Layout()
)

for lay in layout["middle"].children:
    lay.update("Wow!")
console.print(layout)