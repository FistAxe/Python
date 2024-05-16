from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.align import Align
from RPGclass import Data, monster
from typing import List

class Box(Panel):
    def __init__(self, update="Box called without its renderable", name:str="Box"):
        super().__init__(update, title=name, title_align="left")

class Battlefield(Box):
    #Panel(get_battlefield())
    
    event : Layout
    field : Panel
    namespace : Panel

    playerlist : list

    def monsterlayoutgen(self, monsters:List[monster]):
        for i in range(len(monsters)):
            daughterlayout = Layout(name=f"monster {i + 1}")
            yield daughterlayout

    def __init__(self, data:Data=None):
        #data 제대로 들어옴
        if isinstance(data, Data):
            table = Layout()

            table.split_row(
                Layout(name="playerside"),
                Layout(Align("vs", align="center", vertical="middle"), name="middle"),
                Layout(name="monsterside")
            )
            table["middle"].size = 2

            table["playerside"].split_row(
                Layout(name="player 4"),
                Layout(name="player 3"),
                Layout(name="player 2"),
                Layout(name="player 1"),
            )
            
            monsterlist = list(self.monsterlayoutgen(data.monsters))
            table["monsterside"].split_row(*monsterlist)

            for playerlayout in table["playerside"].children:
                playerlayout.split_column(
                    Layout(name=f"{playerlayout.name}_event"),
                    Layout(name=f"{playerlayout.name}_field", size=3),
                    Layout(name=f"{playerlayout.name}_namespace", size=3)
                    )
                print(f"{playerlayout.name}_event")
            
            for monsterlayout in table["monsterside"].children:
                monsterlayout.split_column(
                    Layout(name=f"{monsterlayout.name}_event"),
                    Layout(name=f"{monsterlayout.name}_field", size=3),
                    Layout(name=f"{monsterlayout.name}_namespace",size=3)
                )
            
            for player in data.players:
                table[f"{player.id}_field"].update(Panel(player.icon))
                table[f"{player.id}_namespace"].update(player.name)
            
            for monster in data.monsters:
                table[f"{monster.id}_field"].update(Panel(monster.icon))
                table[f"{monster.id}_namespace"].update(monster.name)
            
            #attrlist = list(self.layoutgen("attr", Data.event_num))
            character_info = Panel("Data")

        elif Data == None:
            table = Panel("No Data input")
            character_info = Panel("No Data input")
        else:
            table = Panel("No Data")
            character_info = Panel("No Data")
        
        insidegrid = Layout()
        insidegrid.split_column(
            Layout(table, name="table"),
            Layout(character_info, name="info")
        )

        insidegrid["info"].size = 6

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
        self.layout["down"].size = 4
        return self.layout

    def dwrite(self, text:str):
        #ui.dialog 자체를 재정의하므로, ui.dialog 밖에서 정의된다.
        #ui.dialog까지만 업데이트. 나머지는 layoutgen이 처리.
        self.dialog.wholetext += text
        self.dialog = Dialog(self.dialog.wholetext)

    def twrite(self, data):
        self.battlefield = Battlefield(data)

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
