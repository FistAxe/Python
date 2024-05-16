from rich import print
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.live import Live
from rich.table import Table

class Box(Panel):
    def __init__(self, update="Box called without its renderable", name:str="Box"):
        super().__init__(update, title=name, title_align="left")

class Battlefield(Box):
    #Panel(get_battlefield())
    
    
    def __init__(self, update:Layout | str = "BF called without its renderable"):
        table = Table("with table data in main")
        character_info = Panel("with info data in main")
        
        insidegrid = Layout()
        insidegrid.split_column(
            Layout(table),
            Layout(character_info)
        )

        super().__init__(insidegrid, name="Battlefield")

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

    def layoutgen(self):
    #Live에서 호출됨. Live(renderable()) 같은 식으로.
        self.layout = Layout()
        self.layout.split_row(
            Layout(name="left"),
            Layout(self.dialog, name="right")
            )
        self.layout["left"].split_column(
            Layout(self.battlefield, name="up"),
            Layout(self.commandbox, name="down"),
            )

        self.layout["right"].size = 50
        self.layout["up"].ratio = 6
        return self.layout

    def dwrite(self, text:str):
        #ui.dialog 자체를 재정의하므로, ui.dialog 밖에서 정의된다.
        #ui.dialog까지만 업데이트. 나머지는 layoutgen이 처리.
        self.dialog.wholetext += text
        self.dialog = Dialog(self.dialog.wholetext)

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

"""
def layoutgen(ui:UI):
    #Live에서 호출됨. Live(renderable()) 같은 식으로.
    ui.layout = Layout()
    ui.layout.split_row(
        Layout(name="left"),
        Layout(ui.dialog, name="right")
        )
    ui.layout["left"].split_column(
        Layout(ui.battlefield, name="up"),
        Layout(ui.commandbox, name="down"),
        )

    ui.layout["right"].size = 50
    ui.layout["up"].ratio = 6
    return ui.layout
"""

console : UI = UI()
