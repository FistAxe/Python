from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.align import Align
from rich import box
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
                #왼쪽, players
                Layout(name="playerside"),
                #중간, "vs"
                Layout(Align("vs", align="center", vertical="middle"), name="middle"),
                #오른쪽, monsters
                Layout(name="monsterside")
            )
            table["middle"].size = 2

            #player는 총 4명.
            table["playerside"].split_row(
                Layout(name="player 4"),
                Layout(name="player 3"),
                Layout(name="player 2"),
                Layout(name="player 1"),
            )
            
            #data의 monster 수만큼 monsterlayout 생성.
            monsterlist = list(self.monsterlayoutgen(data.monsters))
            table["monsterside"].split_row(*monsterlist)

            #각 creature마다 event 칸, field 칸, namespace 칸을 가진다.
            for playerlayout in table["playerside"].children:
                playerlayout.split_column(
                    Layout(name=f"{playerlayout.name}_event"),
                    Layout(name=f"{playerlayout.name}_field", size=3),
                    Layout(name=f"{playerlayout.name}_namespace", size=3)
                    )
            
            for monsterlayout in table["monsterside"].children:
                monsterlayout.split_column(
                    Layout(name=f"{monsterlayout.name}_event"),
                    Layout(name=f"{monsterlayout.name}_field", size=3),
                    Layout(name=f"{monsterlayout.name}_namespace",size=3)
                )
            
            #player의 세부 사항 지정.
            playerindexlist = [1, 2, 3, 4]
            for player in data.players:
                if player.index in playerindexlist:
                    table[f"player {player.index}_field"].update(
                        Panel(Align(f"{player.icon}", align="center"), box=box.HEAVY)
                        )
                    table[f"player {player.index}_namespace"].update(player.name)
                    playerindexlist.remove(player.index)

            for blank in playerindexlist:
                table[f"player {blank}_field"].update(" ")
                table[f"player {blank}_namespace"].update("No player")
                table[f"player {blank}_event"].update(" ")
            
            #monster의 세부 사항 지정.
            for monster in data.monsters:
                table[f"monster {monster.index}_field"].update(
                    Panel(Align(f"{monster.icon}", align="center"), box=box.HEAVY)
                    )
                table[f"monster {monster.index}_namespace"].update(monster.name)
            
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

    dialog : Dialog
    battlefield : Battlefield
    commandbox : CommandBox
    layout : Layout

    def __init__(self):
        self.dialog = Dialog("__init__")
        self.battlefield = Battlefield("__init__")
        self.commandbox = CommandBox("__init__")

    #Live에서 호출할 layout을 생성한다. Live( Layout() ) 같은 식으로.
    def layoutgen(self):
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

    #ui.dialog를 재생성한다.
    def dwrite(self, text:str):
        #ui.dialog 자체를 재정의하므로, ui.dialog 밖에서 정의된다.
        #ui.dialog까지만 업데이트. 나머지는 layoutgen이 처리.
        self.dialog.wholetext += text
        self.dialog = Dialog(self.dialog.wholetext)

    #ui.battlefield를 재생성한다.
    def bwrite(self, data):
        self.battlefield = Battlefield(data)

    #ui.commandbox를 재생성한다.
    def cwrite(self, commandtext:str):
        self.commandbox = CommandBox(commandtext)

#너비, 높이만 주어지면 어디든 쓸 수 있는 텍스트 조정 함수
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

console : UI = UI()
