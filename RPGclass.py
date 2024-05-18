import voicefunc
from typing import Literal, List

class Creature:
    def __init__(self, name:str, icon:str):
        self.name = name
        self.icon = icon

class Monster(Creature):
    index : int

    def __init__(self, name:str, icon:str):
        super().__init__(name, icon)

class Character(Creature):
    index : Literal[0, 1, 2, 3, 4]

    def __init__(self, name:str, icon:str):
        self.index = 0
        super().__init__(name, icon)
    
    def setVoice(self, high=740, middle=455, low=350, sec=0.13):
        self.voice = voicefunc.voice(high, middle, low, sec)

class Event:
    
    class SingleEffect:

        class Effect:
            def __init__(self, effect):
                if effect == 'test':
                    self.typ = 'test'

        name : str
        effect : Effect

        def __init__(self, name, effect):
            self.name = name
            self.effect = self.Effect(effect)

    #무엇(들)이 원인인가?
    origins : List[SingleEffect]
    
    #무엇(들)이 대상인가?
    targets : List[SingleEffect]

    def __init__(self, origin_with_effect:dict, target_with_effect:dict):
        self.origins = []
        self.targets = []
        self.initSingleEvents(origin_with_effect, typ="origin")
        self.initSingleEvents(target_with_effect, typ="target")

    def initSingleEvents(self, entity_and_effect:dict, typ:Literal["origin", "target"]):
        for entity, effect in entity_and_effect.items():
            singleeffect = self.SingleEffect(entity, effect)
            if typ == "origin":
                self.origins.append(singleeffect)
            elif typ == "target":
                self.targets.append(singleeffect)
    

class Data:
    monsters : list[Monster] = []
    players : list[Character] = []
    eventList : list[Event] = []
    
    def __init__(self):
        event = Event(
            {'player':'test'},
            {'monster':'test'}
        )
        self.eventList.append(event)
        self.eventIndexRefresh()
    
    #Event의 수
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
        
    def eventIndexRefresh(self):
        counter = 0
        for event in self.eventList:
            counter += 1
            event.index = counter