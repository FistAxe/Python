from rich.console import Console, Group
from rich.layout import Layout
from rich.panel import Panel
from rich.align import Align
from rich.text import Text
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
    'shield_blue' : '#0D2D46',
    'dark_grey' : '#101010',
    'unselected' : '#909070',
    'highlight_yellow' : '#EEEE80',
    'highlight_red' : '#FF8080'
}

status_emoji = {
    'dead' : '💀',
    'shield' : '🟦',
    'hurt' : '🩸'
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

def get_status_emoji(status:dict):
    emoji = ""
    if 'dead' in status:
        emoji = status_emoji["dead"]
        return emoji
    else:
        emoji = [status_emoji[status_name] for status_name in status_emoji if status_name in status]
        return "".join(emoji)

class Box(Panel):
    def __init__(self, update="Box called without its renderable", name:str="Box"):
        super().__init__(update, title=f"[bold italic]{name}[/bold italic]", title_align="left")

class Battlefield(Box):
    #Panel(get_battlefield())

    #세로 축: 하나의 개체.
    class CreatureLayout(Layout):
        def __init__(self, owner:Creature):
            self.owner = owner
            super().__init__(name=owner.name)

            if not hasattr(self.owner, 'dummy'):
                namespace = Group(
                    self.owner.name,
                    Align(f"{self.owner.HP}/{self.owner.max_HP}", align="center", style=f"{HPcolor(self.owner.HP, self.owner.max_HP)}"),
                    get_status_emoji(self.owner.status)
                    )
            else:
                namespace = "empty"
        
            self.split_column(
                Layout(name=f"{self.owner.name}_event"),
                Layout(Panel(Align(f"{self.owner.icon}", align="center"), box=box.HEAVY), name=f"{self.owner.name}_field", size=3),
                Layout(namespace, name=f"{self.owner.name}_namespace", size=3)
                )

        def add_owner(self, owner:Creature):
            self.owner = owner

    #각 칸: 하나의 effect.
    class EffectLayout(Layout):
        def __init__(self, name:str, effect:Effect):
            self.effect = effect
            super().__init__(name=name)
            if isinstance(self.effect, Effect):
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

                result = ""
                if type(icon) == list:
                    for i, ico in enumerate(icon):
                        result += f"{ico}{colon}{content[i]} "
                else:
                    result = f"{icon}{colon}{content}"

                #event 한 칸 반환
                self.update(
                    Align(
                        result,
                        align="center",
                        vertical="middle",
                        style=f"on {color_code}"
                        )
                    )
            else:
                self.update(" ")

    def creatureLayoutGen(self, iterable:List[Creature]):
        for entity in iterable:
            daughterlayout = self.CreatureLayout(owner=entity)
            yield daughterlayout

    def eventLayoutGen(self, owner:Creature, iterable:List[Event]):
        if iterable == []:
            yield Layout(" ")
        else:
            for index, event in enumerate(iterable):
                daughterlayout = Layout(" ")
                for effect in event.effects:
                    if effect.target == owner:
                        daughterlayout = (Battlefield.EffectLayout(f"event_{index + 1}", effect))
                        break
                yield daughterlayout

    def timeLayoutGen(self, eventList:List[Event]):
        if eventList == []:
            yield Layout("vs")
        else:
            for event in eventList:
                daughterlayout = Layout(" ")
                if hasattr(event, 'time'):
                    daughterlayout.update(Align((f"[bold blue]{event.time}[/bold blue]"), vertical='middle', align='center'))
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
            table["middle"].size = 3

            #player는 총 4명.
            indexed_player = [player for player in data.players if player.index in (1, 2, 3, 4)]
            indexed_player.sort(key = lambda x: x.index, reverse=True)
            playerlist = list(self.creatureLayoutGen(indexed_player))
            table["playerside"].split_row(*playerlist)
            
            #data의 monster 수만큼 monsterlayout 생성.
            monsterlist = list(self.creatureLayoutGen(data.monsters))
            if monsterlist != []:
                table["monsterside"].split_row(*monsterlist)
            else:
                table["monsterside"].update(Align("CLEAR!", align='center', vertical='middle'))

            table["middle"].split_column(
                Layout(name="middle_event"),
                Layout(Align("⌛", vertical='middle'), name="middle_field", size=3),
                Layout(" ", name="middle_namespace", size=3)
            )

            #player의 세부 사항 지정.
            playerindexlist = [1, 2, 3, 4]
            for layout in table["playerside"].children:
                #event update
                table[f"{layout.owner.name}_event"].split_column(
                    *list(self.eventLayoutGen(layout.owner, data.eventList))
                    )
                playerindexlist.remove(layout.owner.index)

            #비어있는 아군의 세부 사항 지정.
            for blank in playerindexlist:
                table[f"player {blank}_field"].update(" ")
                table[f"player {blank}_namespace"].update("Error: no dummy")
                table[f"player {blank}_event"].update(" ")
            
            #Monster의 세부 사항 지정.
            for layout in table["monsterside"].children:
                #event update
                table[f"{layout.owner.name}_event"].split_column(
                    *list(self.eventLayoutGen(layout.owner, data.eventList))
                )

            table["middle_event"].split_column(
                *list(self.timeLayoutGen(data.eventList))
            )

            if data.eventList != []:
                now = data.eventList[0].origin
                if now in data.players:
                    table[f"{now.name}_field"].update(
                        Panel(Align(f"{now.icon}", align="center"), box=box.HEAVY, border_style=f"blink {colorDict['highlight_yellow']}")
                        )
                elif now in data.monsters:
                    table[f"{now.name}_field"].update(
                        Panel(Align(f"{now.icon}", align="center"), box=box.HEAVY, border_style=f"blink {colorDict['highlight_red']}")
                        )

            #Info panel 설정
            if data.smallinfo_type == 'Character':
                smallinfo_list = data.players
            elif data.smallinfo_type == 'Monster':
                smallinfo_list = data.monsters
            smallinfo = Text()
            for creature in smallinfo_list:
                selected = False if creature.index == 0 else True
                if selected == True:
                    smallinfo.append(f"{creature.name:<10}")
                elif 'dead' in creature.status:
                    smallinfo.append(f"{creature.name:<10}", colorDict['HP_red'])
                else:
                    smallinfo.append(f"{creature.name:<10}", colorDict["unselected"])
                emoji = Text(f"{get_status_emoji(creature.status)}")
                emoji.align(align='left', width=8)
                smallinfo.append(emoji)
                if selected == True:
                    smallinfo.append(f"{'No description.' if creature.readyevent == None else creature.readyevent.description}\n")
                else:
                    smallinfo.append("\n")

        elif data == None:
            table = Panel("Data is 'None'")
            smallinfo = "Data is 'None'"
        elif type(data) == str:
            table = Panel(f"{data}")
            smallinfo = " "
        else:
            table = Panel("Data is not 'Data'")
            smallinfo = "Wrong Data"
        
        insidegrid = Layout()
        insidegrid.split_column(
            Layout(table, name="table"),
            Layout(Box(smallinfo, name="Info"), name="smallinfo")
        )

        insidegrid["smallinfo"].size = 6

        super().__init__(insidegrid, name="Battlefield")

class Dialog(Box):
    '''화면 왼쪽의 글 상자. 각종 메시지 출력 담당.\n
       불러오면 wholetext의 내용을 가공해 Panel로 내보낸다.'''

    def __init__(self, text="Dialog called without its renderable", width:int=50, height:int=25):
        text = parse(text, width - 2, height - 3)
        super().__init__(text, name="Dialog")

class CommandBox(Box):
    def __init__(self, commandList:list[Creature]|None = None):
        if commandList == (None or []):
            update = "Press any key"
        elif isinstance(commandList, str):
            update = commandList
        else:
            update = ""
            for entity in commandList:
                update += entity.get_command()
                update += " "
        super().__init__(update, name="CommandBox")

class Info(Box):
    def __init__(self, info:Data="Info called without its renderable"):
        super().__init__(info, name="Info")

class UI(Console):

    dialog : Dialog
    battlefield : Battlefield
    info : Info
    commandbox : CommandBox
    layout : Layout

    def __init__(self, console_width:int, console_height:int):
        super().__init__(width=console_width, height=console_height-1)
        self.dialog = Dialog("__init__")
        self.battlefield = Battlefield("__init__")
        self.commandbox = CommandBox("__init__")
        self.info = Info("__init__")

    def resize(self, console_width, console_height):
        self.width = console_width
        self.height = console_height - 1

    #Live에서 호출할 layout을 생성한다. Live( Layout() ) 같은 식으로.
    def layoutgen(self, mode:str):
        self.layout = Layout()
        self.layout.size = self.height - 1
        self.layout.split_row(
            Layout(name="left"),
            Layout(self.dialog, name="right")
            )
        self.layout["left"].split_column(
            Layout(self.info if mode == 'info' else self.battlefield, name="up"),
            Layout(self.commandbox, name="down"),
            )

        self.layout["right"].size = 50
        self.layout["down"].size = 4
        return self.layout

    def dwrite(self, data:'Data'):
        '''ui.dialog를 재생성한다.'''
        #ui.dialog 자체를 재정의하므로, ui.dialog 밖에서 정의된다.
        #ui.dialog까지만 업데이트. 나머지는 layoutgen이 처리.
        self.dialog = Dialog(data.raw_dialog, width=50, height=self.height)

    def bwrite(self, data):
        '''ui.battlefield를 재생성한다.'''
        self.battlefield = Battlefield(data)

    def iwrite(self, data:'Data'):
        self.info = Info(data.info)

    def cwrite(self, commandList:Data.commandList):
        '''ui.commandbox를 재생성한다.'''
        self.commandbox = CommandBox(commandList)

def parse(text:str, width, height, foreign:bool=True):
    '''너비, 높이만 주어지면 어디든 쓸 수 있는 텍스트 조정 함수'''
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
