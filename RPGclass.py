import voicefunc
from typing import Literal

class creature:
    def __init__(self, name:str, icon:str):
        self.name = name
        self.icon = icon

class monster(creature):
    index : int

    def __init__(self, name:str, icon:str):
        super().__init__(name, icon)

class character(creature):
    index : Literal[0, 1, 2, 3, 4]

    def __init__(self, name:str, icon:str):
        self.index = 0
        super().__init__(name, icon)
    
    def setVoice(self, high=740, middle=455, low=350, sec=0.13):
        self.voice = voicefunc.voice(high, middle, low, sec)

class event:
    pass

class Data:
    monsters : list[monster] = []
    players : list[character] = []
    eventList : list[event] = []
    
    def __init__(self):
        pass
    
    #event의 수
    def event_num(self):
        return len(self.eventList)
    
    #players의 index 오류를 수정하고, index의 빈 자리를 앞쪽부터 반환한다.
    def playerIndexCheck(self):
        indexlist = [1, 2, 3, 4]
        for player in self.players:
            if not hasattr(player, "index"):
                player.index = 0
            
            #index가 1,2,3,4 중 하나라면 그 자리는 차 있다. 중복되는 index는 0으로 초기화한다.
            if player.index in indexlist:
                indexlist.remove(player.index)
            else:
                player.index = 0
        
        #남아있는 자리 중 가장 앞쪽을 반환한다. 없으면 0을 반환한다.
        try:
            return indexlist.pop(0)
        except IndexError:
            return 0