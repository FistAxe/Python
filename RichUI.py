from rich.console import Console, Group
from rich.layout import Layout
from rich.panel import Panel
from rich.align import Align
from rich import box
from RPGclass import Effect, Creature, Event
from RPGdata import Data
from typing import List

colorDict = {
    'background' : "black",
    'bg_test_yellow' : '#616006',
    'bg_damage_red' : '#230603',
    'bg_attack_yellow' : '#202003',
    'HP_green' : '#2DD32D',
    'HP_yellow': '#D3D32D',
    'HP_red' : '#911F1F',
    'shield_blue' : '#0D2D46'
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

def get_status_emoji(status:List[str]):
    emoji = ""
    if 'dead' in status:
        emoji = ":skull:"
        return emoji
    else:
        if 'hurt' in status:
            emoji += ":drop_of_blood:"
        if 'shield' in status:
            emoji += ":blue_square:"
    
        return emoji

class Box(Panel):
    def __init__(self, update="Box called without its renderable", name:str="Box"):
        super().__init__(update, title=f"[bold italic]{name}[/bold italic]", title_align="left")

class Battlefield(Box):
    #Panel(get_battlefield())

    #세로 축: 하나의 개체.
    class CreatureLayout(Layout):
        def add_owner(self, owner:Creature):
            self.owner = owner

    #각 칸: 하나의 effect.
    class EffectLayout(Layout):
        effect : Effect

        def effectPanelgen(self):
            if hasattr(self, 'effect'):
                icon = self.effect.get_Icon()
                if icon == None:
                    icon = "X"
                
                content = self.effect.get_content()
                if content == None:
                    content = ""
                    colon = ''
                else:
                    colon = ':'

                #색의 별명을 얻어 와서
                color = self.effect.get_color()
                #없으면 무색
                if color == None:
                    color = "background"
                #색 별명으로 실제 색을 맨 위 colorDict에서 찾는다.
                try:
                    color_code = colorDict[color]
                except KeyError:
                    color_code = colorDict["background"]
                    print("No such color code!")

                #event 한 칸 반환
                self.update(
                    Align(
                        f"{icon}{colon}{content}",
                        align="center",
                        vertical="middle",
                        style=f"on {color_code}"
                        )
                    )
            else:
                self.update(" ")

    def creatureLayoutGen(self, iterable:List[Creature]):
        for entity in iterable:
            daughterlayout = self.CreatureLayout(name=f"{entity.name}")
            daughterlayout.add_owner(entity)
            yield daughterlayout

    def eventLayoutGen(self, owner:Creature, iterable:List[Event]):
        if iterable == []:
            yield Layout(" ")
        else:
            for index, event in enumerate(iterable):
                daughterlayout = self.EffectLayout(name=f"event_{index + 1}")
                daughterlayout.update("")
                for effect in event.effects:
                    if effect.target == owner:
                        daughterlayout.effect = effect
                        daughterlayout.effectPanelgen()
                yield daughterlayout

    def timeLayoutGen(self, eventList:List[Event]):
        if eventList == []:
            yield Layout("vs")
        else:
            for event in eventList:
                daughterlayout = Layout(" ")
                if hasattr(event, 'time'):
                    daughterlayout.update(Align((f"[bold blue]{event.time}[/bold blue]"), vertical='middle'))
                yield daughterlayout


    def __init__(self, data:Data=None):
        #data 제대로 들어옴
        if isinstance(data, Data):
            table = Layout()

            table.split_row(
                #왼쪽, players
                Layout(name="playerside"),
                #중간, "vs"
                Layout(name="middle"),
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
            monsterlist = list(self.creatureLayoutGen(data.monsters))
            table["monsterside"].split_row(*monsterlist)

            #각 Creature마다 event 칸, field 칸, namespace 칸을 가진다.
            #각 "player i_event", "monster i_event"의 이름 형식
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

            table["middle"].split_column(
                Layout(name="middle_event"),
                Layout(" ", name="middle_field", size=3),
                Layout(" ", name="middle_namespace", size=3)
            )

            #player의 세부 사항 지정.
            playerindexlist = [1, 2, 3, 4]
            for player in data.players:
                if player.index in playerindexlist:
                    #field update
                    table[f"player {player.index}_field"].update(
                        Panel(Align(f"{player.icon}", align="center"), box=box.HEAVY)
                        )
                    #status update
                    if not hasattr(player, 'dummy'):
                        namespace = Group(
                            player.name,
                            Align(f"{player.HP}/{player.max_HP}", align="center", style=f"{HPcolor(player.HP, player.max_HP)}"),
                            get_status_emoji(player.status)
                        )
                    else:
                        namespace = "empty"
                    table[f"player {player.index}_namespace"].update(namespace)
                    #event update
                    table[f"player {player.index}_event"].split_column(
                        *list(self.eventLayoutGen(player, data.eventList))
                    )
                    playerindexlist.remove(player.index)

            #비어있는 아군의 세부 사항 지정.
            for blank in playerindexlist:
                table[f"player {blank}_field"].update(" ")
                table[f"player {blank}_namespace"].update("Error: no dummy")
                table[f"player {blank}_event"].update(" ")
            
            #Monster의 세부 사항 지정.
            for monster in data.monsters:
                #field update
                table[f"{monster.name}_field"].update(
                    Panel(Align(f"{monster.icon}", align="center"), box=box.HEAVY)
                    )
                #status update
                namespace = Group(
                    monster.name,
                    Align(f"{monster.HP}/{monster.max_HP}", align="center", style=f"{HPcolor(monster.HP, monster.max_HP)}"),
                    get_status_emoji(monster.status)
                    )
                table[f"{monster.name}_namespace"].update(namespace)
                #event update
                table[f"{monster.name}_event"].split_column(
                    *list(self.eventLayoutGen(monster, data.eventList))
                )

            table["middle_event"].split_column(
                *list(self.timeLayoutGen(data.eventList))
            )

            #Info panel 설정
            character_info = Panel("Info")

        elif data == None:
            table = Panel("Data is 'None'")
            character_info = Panel("Data is 'None'")
        elif type(data) == str:
            table = Panel(f"{data}")
            character_info = Panel(" ")
        else:
            table = Panel("Data is not 'Data'")
            character_info = Panel("Wrong Data")
        
        insidegrid = Layout()
        insidegrid.split_column(
            Layout(table, name="table"),
            Layout(character_info, name="info")
        )

        insidegrid["info"].size = 6

        super().__init__(insidegrid, name="Battlefield")

class Dialog(Box):

    wholetext : str
    
    def __init__(self, update="Dialog called without its renderable", refresh:bool=False, width:int=45, height:int=25):
        if (refresh == False) and hasattr(self, "wholetext"):
            self.wholetext = self.wholetext + update
        else:
            self.wholetext = update
        
        #if not (hasattr(self, "width") or hasattr(self, "height")):
        #    super().__init__("making width and height")
        self.wholetext = parse(self.wholetext, 48, height - 3)
        
        super().__init__(self.wholetext, name="Dialog")

class CommandBox(Box):
    def __init__(self, commandList:dict[str, str]|str|None = None):
        if commandList == (None or {}):
            update = "Press any key"
        elif isinstance(commandList, str):
            update = commandList
        else:
            update = ""
            for string in commandList.values():
                update += string
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
        self.dialog = Dialog(self.dialog.wholetext, width=self.width, height=self.height)

    #ui.battlefield를 재생성한다.
    def bwrite(self, data):
        self.battlefield = Battlefield(data)

    #ui.commandbox를 재생성한다.
    def cwrite(self, commandList:Data.commandList):
        self.commandbox = CommandBox(commandList)

#너비, 높이만 주어지면 어디든 쓸 수 있는 텍스트 조정 함수
def parse(text:str, width, height, foreign:bool=True):
    #1. 추가된 text에 \n 추가해서 width 맞추기
    buf = text.split('\n')
    line_counter = 0
    while line_counter < len(buf):
        char_num = 0
        wide_num = 0
        for char in buf[line_counter]:
            char_num += 1
            if foreign == True and not char.isascii():
                wide_num += 1
        if char_num + wide_num > width:
            buffer_line = buf[line_counter]
            buf[line_counter] = buffer_line[:width - 1 - wide_num] #len(buf[line_counter]) = 0 ~ (width - 1) = width
            buf.insert(line_counter + 1, (buffer_line[width - wide_num - 1:]))
        line_counter += 1
    #2. text의 \n 조사해서 앞부분의 문장 날리기
    while len(buf) > height:
        buf.pop(0)
    parsedtext = '\n'.join(buf)
    return parsedtext
