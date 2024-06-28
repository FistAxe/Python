from rich.panel import Panel
from rich.text import Text
from rich.console import Group
from rich import print

tit1 = Text('title', style='blue')
tit2 = Text(' aa')
tit = Text()
tit.append(tit1)
tit.append(tit2)
pan = Panel('aaa', title=tit)
print(pan)

text = Text()
text.append("Hello", style="bold magenta")
text.append(" World!")
print(text)