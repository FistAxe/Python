import voicefunc
from typing import Literal, List, Callable, TYPE_CHECKING, Union, Type, Dict

if TYPE_CHECKING:
    from RPGdata import Data

#creature을 target으로 가지는 클래스.
class Effect:
    #public
    target : 'Creature'    #creature의 instance
    #private
    _typ : Literal["fixed", "position"]
    _icon : str
    _value : str
    _color : str

    def __init__(
        self,
        target:'Creature',
        effect_type,
        value:int|None=None,
        atk:str|None=None,
        defence:str|None=None,
        mag:str|None=None,
        mind:str|None=None,
        **kwargs
        ):

        self.target = target

#            for coeff, formula in {'atk':atk, 'defence':defence, 'mag':mag, 'mind':mind}.items():
#                self._value += parse_coeff(coeff, formula)

        if effect_type == 'test':
            self._typ = 'test'
            self._icon = ':gear:'
            self._color = 'bg_test_yellow'
        if effect_type == 'damage':
            self._typ = 'fixed'
            self._icon = ':drop_of_blood:'
            self._value = "[b red]-7[/b red]"
            self._color = 'bg_damage_red'
        if effect_type == 'attack':
            self._typ = 'fixed'
            self._icon = '⚔'
            self._color = 'bg_attack_yellow'

    def get_Icon(self):
        try:
            return self._icon
        except:
            return "X"

    def get_content(self):
        try:
            return self._value
        except:
            return None
            
    def get_color(self):
        try:
            return self._color
        except:
            return None
        
    def execute(self, data:'Data'):
        #self.target.HP - self.value
        if self.target.HP <= 0:
            return False
        else:
            return True

#이벤트. 원인과 효과(들), 대상과 효과(들)을 가진다.
#[(원인 1, 효과 1), (원인 2, 효과 2) ... ] -> [(대상 1, 효과 1), (대상 2, 효과 2) ... ]
class Event:
    #각 effect는 index를 가진 creature 하나를 보유한다!
    effects : List[Effect]
    speed : int = 0
    origin : Union['Character', 'Monster']
    target_with_effect:Dict[str, str]={
        "enemy_1" : "damage_7"
    }

    #화면 상에 있으면 True를 반환하는 트리거.
    def defalt_trigger(self, self_entity:Union['Character', 'Monster'], data:'Data'):
        if self_entity.index > 0:
            return 1
        else:
            return 0
        
    #발동 조건은? -> 우선순위
    trigger_condition : Callable[['Creature', 'Data'], int]  | None = defalt_trigger

    def __init__(self, origin:'Creature', target_with_effect:dict, data:'Data'):
        self.effects = []
        if origin != None:
            self.origin = origin

        if target_with_effect != None:
            self.target_with_effect = target_with_effect
        self.calculate_speed()
        self.calculate_effects(data)

    def calculate_speed(self):
        if hasattr(self.origin, 'speed'):
            self.speed = self.origin.speed
        else:
            self.speed = 0

    def calculate_effects(self, data:'Data'):
        if self.target_with_effect != None:
            for target, effect in self.target_with_effect.items():
                typ, num = target.split('_')
                if typ == 'friend':
                    typ = 'player' if self.origin.typ == 'character' else 'monster'
                elif typ == 'enemy':
                    typ = 'monster' if self.origin.typ == 'monster' else 'character'
                if typ == 'player':
                    target_list = get_list_from(num, 4)
                    for index in target_list:
                        new_effect = Effect(data.players[index], effect)
                        self.effects.append(new_effect)
                elif typ == 'monster':
                    max = len(data.monsters)
                    target_list = get_list_from(num, max)
                    for index in target_list:
                        new_effect = Effect(data.monsters[index], effect)
                        self.effects.append(new_effect)

    def change_trigger(self, callable:Callable|None):
        self.trigger_condition = callable

    def execute_self(self, data:'Data'):
        for effect in self.effects:
            effect.execute(data)

class Creature:
    #중립
    typ : Literal['neutral', 'monster', 'character']= 'neutral'

    def __init__(self, name:str, icon:str, HP:int, key:str|None=None):
        self.name = name
        self.icon = icon
        self.HP = self.max_HP = HP
        self.speed = 1
        self.key = key
        self.command : str = f"Blank {self.name} command"
        self.hascommand : bool = False
        self.available_events : List[Type[Event]]=[]

    def add_key(self, key:str):
        self.key = key

    def get_key(self):
        return self.key
    
    #key와 command창의 str로 이루어진 command tuple을 얻는다.
    def get_command(self):
        if self.hascommand and self.command != None:
            return self.key, self.command
        else:
            return None

    def add_eventClass(self, eventClass:Type[Event]):
        self.available_events.append(eventClass)

    #data의 값을 각 eventClass에 순서대로 대입해, 일단 나오면 그 클래스를 반환한다.
    def get_event(self, data:'Data'):
        for eventClass in self.available_events:
            if eventClass.trigger_condition(self, data):
                event = eventClass(data)
                return event
        return None
    
    def make_info(self):
        return f"{self.name} has no info.\n"

class Monster(Creature):
    typ = 'monster'
    #monster의 특징: 화면에 나옴
    index : int

    class stab(Event):
        pass

    def __init__(self, name:str, icon:str, HP:int, key:str|None=None):
        super().__init__(name, icon, HP, key)
        self.available_events.append(self.stab)

    #기본적으로 command가 없음
    def add_command(self, string:str):
        self.command = string

class Character(Creature):
    typ = 'character'
    #player의 특징: 4명까지 화면에 나옴
    index : Literal[0, 1, 2, 3, 4]
    voiceset : dict = {
        'high' : 740,
        'middle' : 455,
        'low' : 350,
        'sec' : 0.13
    }

    def __init__(self, name:str, icon:str, HP:int, speed:int=1, key:str|None=None, command:str|None=None):
        self.index = 0
        super().__init__(name, icon, HP, key)
        self.speed = speed
        self.hascommand = True
        self.command = command

    #player의 특징: 목소리 나옴
    def setVoice(self, voiceset:dict|None=None):
        if voiceset != None:
            self.voiceset = voiceset
        self.voice = voicefunc.voice(**self.voiceset)

    #data의 값을 각 eventClass에 순서대로 대입해, 일단 나오면 그 클래스를 반환한다. Override.
    def get_event(self, data:'Data'):
        for eventClass in self.available_events:
            if eventClass.trigger_condition(self, data):
                event = eventClass(data)
                return event
        return None
        
def parse_coeff():
    pass

def get_list_from(string:str, max:int):
    numlist = []
    #"monster_" 형 : 전체 범위
    if string == "":
        numlist = range(1,max)
    #"monster_a,b" 형 : 상세 범위
    else:
        buf = string.split(",")
        for num in buf:
            #"monster_i" 형 : i 번째 index.
            if num.isdecimal():
                numlist.append(int(num))
            #"monster_i:j" 형 : i~j 번째 index.
            elif ':' in num:
                buff = num.split(':')
                first = buff[0]
                last = buff[1]
                if first.isdecimal() and last.isdecimal():
                    for i in range(int(first), int(last)):
                        numlist.append(i)
                elif first == "" and last.isdecimal():
                    for i in range(1, int(last)):
                        numlist.append(i)
                elif first.isdecimal() and last == "":
                    for i in range(int(first), max):
                        numlist.append(i)
    #중복 제거
    return list(set(numlist))
