import voicefunc
from typing import Literal, List, Callable, TYPE_CHECKING, Union, Type, Dict

if TYPE_CHECKING:
    from RPGdata import Data

#creature을 target으로 가지는 클래스.
#effect_type, 
class Effect:
    #public
    target : 'Creature'    #creature의 instance
    #private
    _typ : Literal["fixed", "position"]
    _icon : str
    _content : str
    _color : str

    def __init__(self, target:'Creature', effect_type, value:int|None=None):
        self.target = target
        self.value = value

#            for coeff, formula in {'atk':atk, 'defence':defence, 'mag':mag, 'mind':mind}.items():
#                self._value += parse_coeff(coeff, formula)

        if effect_type == 'test':
            self._typ = 'test'
            self._icon = ':gear:'
            self._color = 'bg_test_yellow'
        if effect_type == 'damage':
            self._typ = 'fixed'
            self._icon = ':drop_of_blood:'
            self.value = -7
            self._content = f"[b red]{self.value}[/b red]"
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
            return self._content
        except ValueError:
            return None
            
    def get_color(self):
        try:
            return self._color
        except:
            return None
        
    def execute(self, data:'Data'):
        if type(self.value) == int:
            self.target.HP += self.value
        if self.target.HP <= 0:
            self.target.HP = 0
            self.target.status = 'dead'
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
        
    #발동 조건은? -> 우선순위
    #기본값은 화면 상에 있으면 True를 반환하는 트리거.
    @staticmethod
    def trigger_condition(owner:Union['Character', 'Monster'], data:'Data') -> int :
        if owner.index > 0:
            return 1
        else:
            return 0
        
    def __init__(self, origin:'Creature', data:'Data', target_with_effect:dict=None):
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
        value = None
        if self.target_with_effect != None:
            for target, effect in self.target_with_effect.items():
                typ = target.split('_')
                try:
                    num = typ[1]
                    typ = typ[0]
                except IndexError:
                    num = ""
                if typ == 'self':
                    new_effect = Effect(self.origin, effect)
                    self.effects.append(new_effect)
                    value = new_effect.value
                    pass
                elif typ == 'friend':
                    typ = 'player' if self.origin.typ == 'character' else 'monster'
                elif typ == 'enemy':
                    typ = 'monster' if self.origin.typ == 'monster' else 'player'
                if typ == 'player':
                    target_list = get_list_from(num, 4)
                    for target_index in target_list:
                        for player in data.players:
                            if player.index in [1, 2, 3, 4] and player.index == target_index:
                                new_effect = Effect(player, effect, value)
                                self.effects.append(new_effect)
                elif typ == 'monster':
                    max_index = len(data.monsters)
                    target_list = get_list_from(num, max_index)
                    for index in target_list:
                        try:
                            new_effect = Effect(data.monsters[index - 1], effect, value)
                            self.effects.append(new_effect)
                        except IndexError:
                            pass

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
        self._status = "Status"
        self.command : str = f"Blank {self.name} command"
        self.hascommand : bool = False
        self.available_events : List[Type[Event]]=[]

    @property
    def status(self):
        emoji = ""
        if 'dead' in self._status:
            emoji = "dead"
        elif 'hurt' in self._status:
            emoji += "hurt"
        return emoji
    
    @status.setter
    def status(self, string:str):
        if string in ['dead']:
            self._status = string

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
                event = eventClass(self, data)
                return event
        return None
    
    def make_info(self):
        return f"{self.name} has no info.\n"

class Monster(Creature):
    typ = 'monster'
    #monster의 특징: 화면에 나옴
    index : int
    #지금까지 생성된 monster의 수. 클래스 변수.
    num : int = 0

    monster_events = []
        
    class stab(Event):
        @staticmethod
        def trigger_condition(owner:Union['Character', 'Monster'], data:'Data') -> int :
            if owner.index > 0:
                return 1
            else:
                return 0
            
        target_with_effect = {
            'self' : 'attack',
            'player_1' : 'damage'
        }
            
    class poke(Event):
        @staticmethod
        def trigger_condition(owner:Union['Character', 'Monster'], data:'Data') -> int :
            if owner.index > 1 and owner.index < 4:
                return 2
            else: 
                return 0
            
        target_with_effect = {
            'self' : 'attack',
            'player_2' : 'damage'
        }

    def __init__(self, name:str, icon:str, HP:int, key:str|None=None):
        super().__init__(name, icon, HP, key)
        self.available_events.append(self.poke)
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
