import voicefunc
from typing import Literal

class creature:
    def __init__(self, name:str, icon:str):
        self.name = name
        self.icon = icon

class monster(creature):
    id : str

    def __init__(self, name:str, icon:str):
        super().__init__(name, icon)

class character(creature):
    id : str

    def __init__(self, name:str, icon:str):
        super().__init__(name, icon)
    
    def setVoice(self, high=740, middle=455, low=350, sec=0.13):
        self.voice = voicefunc.voice(high, middle, low, sec)

class Data:
    monsters : list[monster] = []
    players : list[character] = []
    
    def __init__(self):
        pass

    def column_num(self):
        return len(self.monsters) + 5
    
    def initcreature(self, typ:Literal['character', 'monster']):
        if typ == 'character':
            last_index = len(self.players) - 1
            if (last_index < 0) or (last_index > 4):
                print("Not in 0~4 player range!")
            else:
                self.players[last_index].id = f"player {last_index + 1}"


        elif typ == 'monster':
            last_index = len(self.monsters) - 1
            if last_index < 0:
                print("less then 1 monster!")
            else:
                self.monsters[last_index].id = f"monster {last_index + 1}"