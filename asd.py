from rich.console import Console
from rich.layout import Layout

console = Console()

layout = Layout()

# Create a list of Layout objects
layouts = [Layout(name="left"), Layout(name="main"), Layout(name="right")]

# Use the *args syntax to unpack the list into split_row
layout.split_row(*layouts)

console.print(layout)