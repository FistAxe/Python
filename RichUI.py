from rich import print
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.live import Live

class Box(Panel):
    def __init__(self, update="Box called without its renderable", name:str="Box"):
        super().__init__(update, title=name, title_align="left")

class Battlefield(Box):
    def __init__(self, update="BF called without its renderable"):
        super().__init__(update, name="Battlefield")

class Dialog(Box):

    wholetext : str
    def __init__(self, update="Dialog called without its renderable", refresh:bool=False):
        if (refresh == False) and hasattr(self, "wholetext"):
            self.wholetext = self.wholetext + update
        else:
            self.wholetext = update
        
        #if not (hasattr(self, "width") or hasattr(self, "height")):
        #    super().__init__("making width and height")
        self.wholetext = parse(self.wholetext, 45, 20)
        
        super().__init__(self.wholetext, name="Dialog")

class CommandBox(Box):
    def __init__(self, update="CB called without its renderable"):
        super().__init__(update, name="CommandBox")

class UI(Console):

    dialog : Dialog #is Panel with methods
    battlefield : Battlefield
    commandbox : CommandBox
    layout : Layout

    def __init__(self):
        self.dialog = Dialog("__init__")
        self.battlefield = Battlefield("__init__")
        self.commandbox = CommandBox("__init__")

def dwrite(ui:UI, text:str):
    #ui.dialog까지만 업데이트. 나머지는 layoutgen이 처리.
    ui.dialog.wholetext += text
    ui.dialog = Dialog(ui.dialog.wholetext)

def parse(text:str, width, height):
    #1. 추가된 text에 \n 추가해서 width 맞추기
    buf = text.split('\n')
    for col in range(len(buf)):
        while len(buf[col]) > width:
            line = buf[col]
            buf[col] = line[:width - 1] #len(bug[col]) = 0 ~ (width - 1) = width
            buf.insert(col + 1,(line[width:]))
    #2. text의 \n 조사해서 앞부분의 문장 날리기
    while len(buf) > height:
        buf.pop(0)
    parsedtext = '\n'.join(buf)
    return parsedtext

    return buf

def layoutgen(ui:UI):
    #Live에서 호출됨.
    layout = Layout()
    layout.split_row(
        Layout(name="left"),
        Layout(ui.dialog, name="right")
        )
    layout["left"].split_column(
        Layout(ui.battlefield, name="up"),
        Layout(ui.commandbox, name="down"),
        )

    layout["right"].size = 50
    layout["up"].ratio = 6
    return layout

console : UI = UI()
