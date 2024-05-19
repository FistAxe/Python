from rich.console import Console, Group
from rich.layout import Layout
from rich.panel import Panel
from rich.align import Align
from rich import box
from RPGclass import Data, Monster, Event, Character, Choice
from typing import List, Literal

colorDict = {
    'bg_test_yellow' : '#616006',
    'bg_damage_red' : '#230603',
    'bg_attack_yellow' : '#202003',
    'HP_green' : '#2DD32D',
    'HP_yellow': '#D3D32D',
    'HP_red' : '#911F1F'
}

def HPcolor(HP:int, max_HP:int):
    HPratio = HP / max_HP
    if HPratio > 0.5:
        return f"#{hex(int((0x2D/0xD3)*(HPratio - 0.5)*2 + 0x2D))[2:]}D32D"
    else :
        return (
            f"#{hex(int((0x91/0xD3)*HPratio*2 + 0x91))[2:]}" +
            f"{hex(int((0x1F/0xD3)*HPratio*2 + 0x1F))[2:]}" +
            f"{hex(int((0x1F/0xD3)*HPratio*2 + 0x1F))[2:]}"
            )


class Box(Panel):
    def __init__(self, update="Box called without its renderable", name:str="Box"):
        super().__init__(update, title=name, title_align="left")

class Battlefield(Box):
    #Panel(get_battlefield())

    def monsterlayoutgen(self, monsters:List[Monster]):
        for i in range(len(monsters)):
            daughterlayout = Layout(name=f"monster {i + 1}")
            yield daughterlayout

    def eventlayoutgen(self, creature:Character|Monster, eventList:List[Event]):
        if isinstance(creature, Character):
            typ = "player"
        else:
            typ = "monster"
        index = creature.index

        event_num = 1
        for event in eventList:
            #event의 수만큼 캐릭터 위에 줄을 만든다.
            daughterlayout = Layout(name=f"{typ}_{index}_event_{event_num}")
            #초기화.
            daughterlayout.update("")
            
            #이벤트의 모든 원인에 대해:
            for origin in event.origins:
                if (
                    #대상의 이름이 creature의 이름에 포함되거나:
                    origin.target in creature.name or
                    #대상의 위치가 creature의 위치에 포함되면:
                    origin.target in f"{typ}_{index}"
                    ):
                    #대상의 effect를 layout에 반영한다.
                    daughterlayout.update(self.eventPanelgen(origin))
            
            #이벤트의 모든 대상에 대해:
            for target in event.targets:
                if (
                    #대상의 이름이 creature의 이름에 포함되거나:
                    target.target in creature.name or
                    #대상의 위치가 creature의 위치에 포함되면:
                    target.target in f"{typ}_{index}"
                    ):
                    #대상의 effect를 layout에 반영한다.
                    daughterlayout.update(self.eventPanelgen(target))

            #이벤트 index 증가.
            event_num += 1
            yield daughterlayout

    def eventPanelgen(self, single_effect:Event.SingleEffect):
        icon = single_effect.get_Icon()
        if icon == None:
            icon = ""
        content = single_effect.get_content()
        if content == None:
            content = ""
            colon = ''
        else:
            colon = ':'
        color = single_effect.get_color()
        if color == None:
            color = ""
        try:
            color_code = colorDict[color]
        except KeyError:
            print("No such color code!")

        return Align(f"{icon}{colon}{content}", align="center", vertical="middle", style=f"on {color_code}")

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

            #각 Creature마다 event 칸, field 칸, namespace 칸을 가진다.
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
                    namespace = Group(
                        player.name,
                        Align(f"{player.HP}/{player.max_HP}", align="center", style=f"{HPcolor(player.HP, player.max_HP)}"),
                        "Status"
                    )
                    table[f"player {player.index}_namespace"].update(namespace)
                    table[f"player {player.index}_event"].split_column(
                        *list(self.eventlayoutgen(player, data.eventList))
                    )
                    playerindexlist.remove(player.index)

            for blank in playerindexlist:
                table[f"player {blank}_field"].update(" ")
                table[f"player {blank}_namespace"].update("No player")
                table[f"player {blank}_event"].update(" ")
            
            #Monster의 세부 사항 지정.
            for monster in data.monsters:
                table[f"monster {monster.index}_field"].update(
                    Panel(Align(f"{monster.icon}", align="center"), box=box.HEAVY)
                    )
                namespace = Group(
                    monster.name,
                    Align(f"{monster.HP}/{monster.max_HP}", align="center", style=f"{HPcolor(monster.HP, monster.max_HP)}"),
                    "Status"
                    )
                table[f"monster {monster.index}_namespace"].update(namespace)
                table[f"monster {monster.index}_event"].split_column(
                    *list(self.eventlayoutgen(monster, data.eventList))
                )

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
    def __init__(self, choiceList:dict[str, Choice]|str|None = None):
        if choiceList == (None or {}):
            update = "Press any key"
        elif type(choiceList) == str:
            update = choiceList
        else:
            update = ""
            for choice in choiceList.values():
                command_str = choice.string
                update += command_str
                update += " "
        super().__init__(update, name="CommandBox")

class UI(Console):

    dialog : Dialog
    battlefield : Battlefield
    commandbox : CommandBox
    layout : Layout

    def __init__(self, console_width:int, console_height:int):
        super().__init__(width=console_width, height=console_height-1)
        self.dialog = Dialog("__init__")
        self.battlefield = Battlefield("__init__")
        self.commandbox = CommandBox("__init__")

    def resize(self, console_width, console_height):
        self.width = console_width
        self.height = console_height - 1

    #Live에서 호출할 layout을 생성한다. Live( Layout() ) 같은 식으로.
    def layoutgen(self):
        self.layout = Layout()
        self.layout.size = self.height - 1
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
    def cwrite(self, choiceList:Data.choiceList):
        self.commandbox = CommandBox(choiceList)

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
