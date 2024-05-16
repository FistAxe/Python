import voicefunc

class creature:
    def __init__(self, name:str, icon:str):
        self.name = name
        self.icon = icon

class monster(creature):
    def __init__(self, name:str, icon:str):
        super().__init__(name, icon)

class character(creature):
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