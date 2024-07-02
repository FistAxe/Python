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
    _modifier : List

    @classmethod
    def modify(cls, modifier=None):
        class ModifiedEffect(cls):
            pass
        new_effect = ModifiedEffect
        new_effect._modifier = modifier
        return new_effect
    
    def __init__(self, target:'Creature', effect_type:str|None=None, value:int|None=None, origin:Union['Creature', None]=None):
        self.apply(target, effect_type, value, origin)
    
    def apply(self, target:'Creature', effect_type:str|None=None, value:int|None=None, origin:Union['Creature', None]=None):
        self.target = target
        self.origin = origin
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
            self.target.isDead()
            return None
        else:
            return "No value in effect!\n"

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
    target_with_effect:Dict[str, str|Effect|tuple]={
        "self" : "test"
    }
    '''{ '대상1 str' : '효과1 str', ...}'''
    description : str = 'dummy event.'
        

    @staticmethod
    def trigger_condition(owner:Union['Character', 'Monster'], data:'Data') -> int :
        '''Override할 것. 정수 우선순위를 반환한다. 기본값은 owner가 화면 상에 있으면 1을 반환.'''
        if owner.index > 0:
            return 1
        else:
            return 0
        
    def __init__(self, origin:Union['Creature', None], data:'Data', target_with_effect:dict|None=None):
        '''Event 주인, 전체 data, dict 형식의 target과 effect.'''
        self.effects = []
        self.origin = origin

        if target_with_effect != None:
            self.target_with_effect = target_with_effect

        if origin != None:
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
                                new_effect = self.make_effect(player, effect)
                                self.effects.append(new_effect)
                elif typ == 'monster':
                    target_list = get_list_from(num, len(data.monsters))
                    for index in target_list:
                        try:
                            new_effect = self.make_effect(data.monsters[index - 1], effect)
                            self.effects.append(new_effect)
                        except IndexError:
                            pass
    
    def make_effect(self, target:'Creature', effect:Effect|tuple|str):
        '''Effect의 instance를 반환한다.'''
        #Effect instance 아님, effect_type 제공해 생성
        if type(effect) is str:
            return Effect(target, effect_type=effect, origin=self.origin)
        #Effect instance, 주어진 instance 사용
        elif type(effect) is tuple:
            e = effect[0].modify(*effect[1:])
            return e(target, origin=self.origin)
        elif issubclass(effect, Effect):
            return effect(target, origin=self.origin)
        else:
            raise TypeError

    def change_trigger(self, callable:Callable|None):
        self.trigger_condition = callable

    def execute_self(self, data:'Data'):
        log = ""
        if 'dead' not in self.origin.status:
            for effect in self.effects:
                log += new_log if (new_log := effect.execute(data)) != None else ""
        return log

class SingleBuff(Effect):
    buff_dict = {
        'shield' : ('[bold]:blue_square:[/bold]', 'b blue'),
        'poison' : ('p', "b purple")
    }

    def __init__(self, target: Union['Character', 'Monster']):
        self.target = target
        self._color = 'dark_grey'

    def get_buffname(self):
        return [key for key in self.target.status if self.buff_dict.get(key) != None]
    
    def contentgen(self, value:int, color:str):
        return f"[{color}]{'+' if value > 0 else '' }{value}[/{color}]"

    def get_Icon(self):
        return [self.buff_dict[key][0] for key in self.get_buffname()]

    def get_content(self):
        return [self.contentgen(value=self.target.status.get(key), color=self.buff_dict[key][1]) for key in self.get_buffname()]
    
    def execute(self, data:'Data'):
        pass

class Buff(Event):
    target_with_effect = {}

    @staticmethod
    def trigger_condition(owner: Union['Character', 'Monster'], data: 'Data') -> int:
        return 0

    def __init__(self, data: 'Data'):
        super().__init__(origin=None, data=data, target_with_effect=None)
        self.time = " "

    def refresh_buff(self, data:'Data'):
        self.effects = []
        bufftargets = [creature for creature in data.players + data.monsters if creature.index != 0 and creature.status != {}]
        for bufftarget in bufftargets:
            self.effects.append(SingleBuff(bufftarget))

    def execute_self(self, data: 'Data'):
        log = ""
        for effect in self.effects:
            log += effect.execute(data)
        return log if log != "" else None

class Creature:
    #중립
    typ : Literal['neutral', 'monster', 'character']= 'neutral'
    status : dict[str, bool|int|None]
    is_active : True
    possible_status_list = [
        'dead',
        'shield',
        'hurt'
    ]
    description = "A sample Creature object."

    def __init__(self, name:str, icon:str, HP:int, key:str|None=None):
        self.name = name
        self.icon = icon
        self.HP = self.max_HP = HP
        self.speed = 1
        self.atk = 0

        self.key = key
        self.status = {}
        self.command : str = f"Blank {self.name} command"
        self.available_events : List[Type[Event]]=[]
        self.status_duration_list : list[Dict[Literal['name', 'turn', 'value'], int|str]] = []
        '''name:status 이름, turn:남은 턴 수, value:복귀할 양'''
        self.readyevent : Event|None = None
    
    def add_status(self, string:str, value:int|None, turn:int|None=None):
        if string == 'dead':
            self.status = {'dead' : True}
        elif string in self.possible_status_list:
            self.status[string] = self.status.get(string, 0) + value
            if turn != None:
                self.status_duration_list.append({"name" : string, "turn" : turn, "value" : value})
        else:
            return "No such status name!\n"
        
    def check_status_turn(self):
        for lst in self.status_duration_list[:]:
            lst['turn'] -= 1
            if lst['turn'] <= 0:
                self.status[lst['name']] -= lst['value']
                self.status_duration_list.remove(lst)
                if self.status[lst['name']] <= 0:
                    del(self.status[lst['name']])

    def calculate_HP(self, damage:int):
        '''직후 isDead() 호출을 권장.'''
        if 'shield' in self.status:
            self.status['shield'] += damage
            if self.status['shield'] <= 0:
                damage = self.status['shield']
                self.status.pop('shield')
            else:
                damage = 0
                
        self.HP += damage
    
    def isDead(self):
        if 'dead' in self.status:
            return True
        elif self.HP <= 0:
            self.HP = 0
            self.status = {'dead' : True}
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
    
    def has_command(self, phase:str, main_mode:str):
        '''기본적으로 command가 없음'''
        return False
    
    def get_command(self):
        '''command 설명을 얻는다.'''
        if self.command != None:
            return self.command
        else:
            return ""

    def add_eventClass(self, eventClass:Type[Event]):
        self.available_events.append(eventClass)

    def get_event(self, data:'Data'):
        '''data의 값을 자신의 eventClass에 순서대로 대입해, 가장 높은 우선순위의 eventClass를 반환한다.'''
        priority = 0
        event = None
        for eventClass in self.available_events:
            buf_prior = eventClass.trigger_condition(self, data)
            if buf_prior > priority:
                priority = buf_prior
                event = eventClass(self, data)
        self.readyevent = event
        return event
    
    def make_info(self):
        return f"{self.name} has no info.\n"

class Monster(Creature):
    typ = 'monster'
    
    index : int
    '''monster의 특징: 화면에 나옴'''

    num : int = 0
    '''지금까지 생성된 monster의 수. 클래스 변수.'''

    description = "A sample Monster object."
        
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
    description = "A sample Character object."

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

    def has_command(self, phase:str, main_mode:str):
        if phase == 'select' and 'dead' not in self.status:
            return True
        elif phase == 'process':
            return False
        else:
            return False
        
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