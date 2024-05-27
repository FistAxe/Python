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
    _content : str
    _color : str

    def __init__(self, target:'Creature', effect_type:str|None=None, value:int|None=None):
        self.target = target
        self.value = 0 if value == None else value

#       for coeff, formula in {'atk':atk, 'defence':defence, 'mag':mag, 'mind':mind}.items():
#           self._value += parse_coeff(coeff, formula)
        #디버그용 기본 effect들.
        if effect_type == 'test' or None:
            self._typ = 'test'
            self._icon = ':gear:'
            self._color = 'bg_test_yellow'
        elif effect_type == 'damage':
            self._typ = 'fixed'
            self._icon = ':drop_of_blood:'
            self.value = -7
            self._content = f"[b red]{self.value}[/b red]"
            self._color = 'bg_damage_red'
        elif effect_type == 'attack':
            self._typ = 'fixed'
            self._icon = '⚔'
            self._color = 'bg_attack_yellow'
            self._content = ''

    def get_Icon(self):
        if hasattr(self, '_icon'):
            return self._icon
        else:
            return "X"

    def get_content(self):
        if hasattr(self, '_content'):
            return self._content
        else:
            return None
            
    def get_color(self):
        if hasattr(self, '_color'):
            return self._color
        else:
            return None
        
    def execute(self, data:'Data'):
        if type(self.value) == int:
            self.target.calculate_HP(self.value)
            return self.target.isDead()

class Event:
    '''이벤트. original_speed, target_with_effect를 가진다.\n
        초기화 시 origin, data를 필요로 하며, speed, effects[]가 계산되어 추가된다.'''
    effects : List[Effect]
    original_speed : int = 0
    '''이벤트 속도 보정치. owner의 속도와 같이 set_speed에서 계산해 speed를 구한다.'''
    speed : int = 0
    '''실제 이용되는 속도.'''
    origin : Union['Character', 'Monster']
    '''이벤트의 원인.'''
    target_with_effect:Dict[str, str]={
        "enemy_1" : "damage_7"
    }
    '''{ '대상1 str' : '효과1 str', ...}'''
        

    @staticmethod
    def trigger_condition(owner:Union['Character', 'Monster'], data:'Data') -> int :
        '''Override할 것. 정수 우선순위를 반환한다. 기본값은 owner가 화면 상에 있으면 1을 반환.'''
        if owner.index > 0:
            return 1
        else:
            return 0
        
    def __init__(self, origin:'Creature', data:'Data', target_with_effect:dict|None=None):
        '''Event 주인, 전체 data, dict 형식의 target과 effect.'''
        self.effects = []
        if origin != None:
            self.origin = origin

        if target_with_effect != None:
            self.target_with_effect = target_with_effect
        self.set_speed()
        self.calculate_effects(data)


    def set_speed(self):
        '''SubEvent에서 override할 것. 기본 속도는 origin의 속도.'''
        if hasattr(self.origin, 'speed'):
            self.speed = self.origin.speed + self.original_speed
            if self.speed < 0:
                self.speed = 0
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
                    typ = typ[0]
                if typ == 'self':
                    new_effect = self.make_effect(self.origin, effect)
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
                                new_effect = self.make_effect(player, effect, value)
                                self.effects.append(new_effect)
                elif typ == 'monster':
                    max_index = len(data.monsters)
                    target_list = get_list_from(num, max_index)
                    for index in target_list:
                        try:
                            new_effect = self.make_effect(data.monsters[index - 1], effect, value)
                            self.effects.append(new_effect)
                        except IndexError:
                            pass
    
    def make_effect(self, player:'Creature', effect:Effect|str, value:int|None=None):
        '''Effect의 instance를 반환한다.'''
        if type(effect) is str:
            return Effect(player, effect, value)
        elif issubclass(effect, Effect):
            return effect(player, value)
        else:
            raise TypeError

    def change_trigger(self, callable:Callable|None):
        self.trigger_condition = callable

    def execute_self(self, data:'Data'):
        if 'dead' not in self.origin._status:
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
        self._status = []
        self.command : str = f"Blank {self.name} command"
        self.available_events : List[Type[Event]]=[]

    @property
    def status(self):
        return self._status
    
    @status.setter
    def status(self, string:str):
        if string == 'dead':
            self._status = ['dead']
        elif 'hurt' in string and 'hurt' not in self._status:
            self._status.append('hurt')
        elif 'shield' in string and 'shield' not in self._status:
            self._status.append('shield')

    def calculate_HP(self, damage:int):
        '''직후 isDead() 호출을 권장.'''
        if hasattr(self, 'shield_effect'):
            damage = self.shield_effect.calculate_shield(damage)
        self.HP += damage
    
    def isDead(self):
        if 'dead' in self.status:
            return True
        elif self.HP <= 0:
            self.HP = 0
            self.status = 'dead'
            return True
        else:
            return False

    def add_key(self, key:str):
        self.key = key

    def get_key(self):
        if 'dead' not in self.status:
            return self.key
        else:
            return None
    
    def has_command(self, mode:str):
        return False
    
    def get_command(self, mode:str):
        '''key와 command창의 str로 이루어진 command tuple을 얻는다.'''
        if self.has_command(mode) and self.command != None:
            return self.key, self.command
        else:
            return None

    def add_eventClass(self, eventClass:Type[Event]):
        self.available_events.append(eventClass)

    def get_event(self, data:'Data'):
        '''data의 값을 자신의 eventClass에 순서대로 대입해, 일단 나오면 그 클래스를 반환한다.'''
        for eventClass in self.available_events:
            if eventClass.trigger_condition(self, data):
                event = eventClass(self, data)
                return event
        return None
    
    def make_info(self):
        return f"{self.name} has no info.\n"

class Monster(Creature):
    typ = 'monster'
    
    index : int
    '''monster의 특징: 화면에 나옴'''

    num : int = 0
    '''지금까지 생성된 monster의 수. 클래스 변수.'''
        
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

        def get_speed(self):
            return 5
            
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

        def get_speed(self):
            return 7

    skillList : Event = [stab, poke]

    def __init__(self, name:str, icon:str, HP:int, key:str|None=None):
        super().__init__(name, icon, HP, key)
        self.available_events.extend(self.skillList)

    def has_command(self, mode:str):
        '''기본적으로 command가 없음'''
        return False

    def add_command(self, string:str):
        self.command = string

class Character(Creature):
    typ = 'character'
    index : Literal[0, 1, 2, 3, 4]
    '''player의 특징: 4명까지 화면에 나옴'''
    voiceset : dict = {
        'high' : 740,
        'middle' : 455,
        'low' : 350,
        'sec' : 0.13
    }
    '''high, middle, low, sec'''

    def __init__(self, name:str, icon:str, HP:int, speed:int=1, key:str|None=None, command:str|None=None, skillList:List[Event]|None = None):
        self.index = 0
        super().__init__(name, icon, HP, key)
        self.speed = speed
        self.command = command
        if skillList != None:
            self.available_events = skillList

    #player의 특징: 목소리 나옴
    def setVoice(self, voiceset:dict|None=None):
        if voiceset != None:
            self.voiceset = voiceset
        self.voice = voicefunc.voice(**self.voiceset)

    def has_command(self, mode:str):
        if mode == 'select' and 'dead' not in self.status:
            return True
        elif mode == 'process':
            return False
        else:
            return False

    #data의 값을 각 eventClass에 순서대로 대입해, 일단 나오면 그 클래스를 반환한다. Override.
    def get_event(self, data:'Data'):
        for eventClass in self.available_events:
            if eventClass.trigger_condition(self, data):
                event = eventClass(self, data)
                return event
        return None
        
def parse_coeff():
    pass

def get_list_from(string:str, max:int):
    numlist = []
    #"monster_" 형 : 전체 범위
    if string == "":
        numlist = range(1, max + 1)
    #"monster_a,b" 형 : 상세 범위
    else:
        buf = string.split(",")
        for num in buf:
            #"monster_i" 형 : i 번째 index.
            if num.isdecimal():
                intnum = int(num)
                if intnum < 0:
                    intnum = max + intnum + 1
                numlist.append(intnum)
            #"monster_i:j" 형 : i~j 번째 index.
            elif ':' in num:
                buff = num.split(':')
                first = buff[0]
                last = buff[1]
                if first.isdecimal() and last.isdecimal():
                    for i in range(int(first), int(last) + 1):
                        numlist.append(i)
                elif first == "" and last.isdecimal():
                    for i in range(1, int(last) + 1):
                        numlist.append(i)
                elif first.isdecimal() and last == "":
                    for i in range(int(first), max + 1):
                        numlist.append(i)
    #중복 제거
    return list(set(numlist))

if __name__ == '__main__':
    print(get_list_from('2,2:', 4))
