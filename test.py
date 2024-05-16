from rich import print
from rich.layout import Layout

layout = Layout()

layout.split_row(
    Layout(name="left"),
    Layout(name="right")
)

layout["left"].split_column(
    Layout(name="up"),
    Layout(name="down")
)
layout["up"].split_row(
    Layout(name="leftleft"),
    Layout(name="rightright")
)

layout["right"].update("right")
layout["up"].update("up")
layout["leftleft"].update("leftleft")

print(layout)