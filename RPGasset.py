from RPGclass import Character, Creature, Event, Monster, Effect
from RPGdata import Data
from typing import Callable

# coefficient={'type1':'coeff1', 'type2':'coeff2', ... } : value에 수정되는 값. type의 값*coeff 만큼이 value에 더해진다.

#'self' : 자기 자신.
#'player_i : i번째 아군.
#'monster_i : i번째 적군. i<0일 시 뒤에서부터. i=0일 시 화면에 없는 적 대상.
#'p_least_attr' : attr이 가장 적은 대상.
#'p_most_attr' : attr이 가장 큰 대상.

#*******자기 자신에게***********
#"attack" : 공격. 방해 불가.
#"move_i" : 이벤트 종료 후 i만큼 이동.
#"move_to_i" : 이벤트 종료 후 i 위치로 이동.
#"focus_damage" : 집중. damage 이상 공격 받으면 방해 가능.

#*******상대에게****************
#"heal" : 회복.
#"damage" : 공격받음. 최종 value만큼 HP에 피해를 받는다.
#   value : int -> 특정 수치만큼.

#   value : melee -> value에 공격자의 물리 공격력 대입.


#melee = Event.Effect("damage", atk='*1')

#heal = Event.Effect(
#    {'least' : "heal_"}
#)

#SubEffect 추가
'''
class SubEffect(Effect):
    def __init___(self, target:Creature, value:int):
        self.target = target
        self.value = 0 if value == None else value

#       for coeff, formula in {'atk':atk, 'defence':defence, 'mag':mag, 'mind':mind}.items():
#           self._value += parse_coeff(coeff, formula)

        self._typ = 'fixed' or 'position'
        self._icon = '<single character>'
        self.value += coefficient
        self._content = f"[b red]{self.value}[/b red]"
        self._color = '<color name>'

    def execute(self, data:Data):
        if type(self.value) == int:
            self.target.HP += self.value
        return self.target.isDead()
'''

class MeleeDamage(Effect):
    atk_modifier : Callable[[int], int]|None = None

    @classmethod
    def modify(self, atk_modifier:Callable[[int], int]|None=None):
        new_class = super().modify()
        if atk_modifier != None:
            new_class.atk_modifier = atk_modifier
        return new_class

    def __init__(self, target: Creature, value: int | None = None, origin: Creature|None = None):
        self.target = target

        if value != None:
            self.value = value
        elif origin != None:
            self.origin = origin
            if hasattr(self.origin, 'atk') and hasattr(self, 'atk_modifier'):
                if self.atk_modifier == None:
                    self.value = 0 - self.origin.atk
                else:
                    self.value = 0 - int(self.atk_modifier(self.origin.atk))
            else:
                self.value = 0

        self._icon = '⚔️'
        self._color = 'bg_damage_red'
        self._content = f'[b red]{self.value}[/b red]'

class PrepareShield(Effect):

    @classmethod
    def modify(cls, fixed:int|None=None, modifier:Callable|None=None):
        new_class = super().modify(modifier)
        new_class.value = fixed if fixed != None else 10
        return new_class

    def __init__(self, target: Creature, value: int | None = None, origin=None):
        self.target = target
        self.origin = origin
        if value != None:
            self.value += value

        self._typ = 'fixed'
        self._icon = '🟦'
        self._color = 'shield_blue' if target != origin else 'bg_attack_yellow'
        self._content = f"[b blue]{'+' if self.value > 0 else '' }{self.value}[/b blue]"

    def execute(self, data: Data):
        return self.target.add_status('shield', self.value, 1)

#trigger 추가
def index_trigger(owner:Character|Monster, index:int):
    return 1 if owner.index == index else 0

#SubEvent 추가
'''
class SubEvent(Event):
        @staticmethod
        def trigger_condition(owner:Union['Character', 'Monster'], data:'Data') -> int :
            우선순위 반환 조건문. 해당 없으면 0 반환.
            
        target_with_effect = {
            'self' : 'effect_type',
            '대상 1' : '효과 종류',
            '대상 2' : '효과 종류'.
            ...
        }
'''
#SubMonster 추가
'''
class SubMonster(Monster):
    name = str
    icon = str 한 글자
    HP = 숫자
    key = None, 상호작용 넣고 싶다면 넣을 것.

    #skillList 재정의
    skillList : Event = [Subevent_1. Subevent_2, ...]

    def __init__(self):
        super().__init__(name, icon, HP, key)
        ...

'''

class Goblin(Monster):
    name = 'goblin'
    icon = 'G'
    HP = 6

    class stab(Event):
        original_speed = 1

        @staticmethod
        def trigger_condition(owner:Monster, data:'Data') -> int :
            return index_trigger(owner, 1)
            
        target_with_effect = {
            'self' : 'attack',
            'player_1' : 'damage'
        }
            
    class poke(Event):
        original_speed = 4

        @staticmethod
        def trigger_condition(owner:Monster, data:'Data') -> int :
            if owner.index > 1 and owner.index < 4:
                return 2
            else: 
                return 0
            
        target_with_effect = {
            'self' : 'attack',
            'player_2' : 'damage'
        }

    skillList = [stab, poke]

    def __init__(self, key: str | None = None):
        super().__init__(self.name, self.icon, self.HP, key)

#Character 추가
class Andrew(Character):
    def __init__(self):
        super().__init__(
            name = 'Andrew',
            icon = 'A',
            HP = 12,
            key = 'a',
            speed = 4,
            command = "(A)ndrew",
            skillList=self.skillList
        )
        self.atk = 7

    class A_Protect(Event):
        original_speed = -3
        description = "Shield. Yield shield to get 10 shield."

        @staticmethod
        def trigger_condition(owner: Character | Monster, data: Data) -> int:
            return index_trigger(owner, 1)
   
        target_with_effect = {
            'self' : (PrepareShield, 10)
        }

    class A_SingleHit(Event):
        original_speed = 2
        description = 'Attack the most front enemy with melee damage.'

        @staticmethod
        def trigger_condition(owner: Character | Monster, data: Data) -> int:
            return index_trigger(owner, 2)

        target_with_effect = {
            'self' : 'attack',
            'monster_1' : MeleeDamage
        }

    class A_MultiHit(Event):
        original_speed = 4
        description = 'Attack all enemys with melee damage.'

        @staticmethod
        def trigger_condition(owner: Character | Monster, data: Data) -> int:
            return index_trigger(owner, 3)

        target_with_effect = {
            'self' : 'attack',
            'monster_' : MeleeDamage
        }

    class A_Backup(Event):
        original_speed = 6
        description = 'attacks the most far enemy with melee damage.'

        @staticmethod
        def trigger_condition(owner: Character | Monster, data: Data) -> int:
            return index_trigger(owner, 4)

        target_with_effect = {
            'self' : 'attack',
            'monster_-1' : MeleeDamage
        }
    
    skillList = [A_Protect, A_SingleHit, A_MultiHit, A_Backup]

class Brian(Character):
    def __init__(self):
        super().__init__(
            name = 'Brian',
            icon = 'B',
            HP = 10,
            key = 'b',
            speed = 2,
            command = "(B)rian",
            skillList = self.skillList
        )
        self.atk = 5

    class B_Assult(Event):
        original_speed = -1
        description = 'Assult the closest enemy with melee damage.'

        @staticmethod
        def trigger_condition(owner: Character | Monster, data: Data) -> int:
            return index_trigger(owner, 1)
        
        target_with_effect = {
            'self' : 'attack',
            'monster_1' : (MeleeDamage, (lambda effect, atk:atk*1.2))
        }

    class B_BasicAttack(Event):
        original_speed = 4
        description = 'Normal attack. Slow and weak. x0.5 melee damage.'

        @staticmethod
        def trigger_condition(owner: Character | Monster, data: Data) -> int:
            return index_trigger(owner, 2)
        
        target_with_effect = {
            'self' : 'attack',
            'monster_2' : (MeleeDamage, (lambda effect, atk:atk*0.5))
        }

    class B_Revenge(Event):
        original_speed = 3
        description = 'Attacks 2nd enemy. If enemy is inactive, x1.5 melee dmg.'

        @staticmethod
        def trigger_condition(owner: Character | Monster, data: Data) -> int:
            return index_trigger(owner, 3)
        
        target_with_effect = {
            'self' : 'attack',
            'monster_2' : (MeleeDamage, (lambda effect, atk:atk*1.5))
        }

    class B_Ambush(Event):
        original_speed = 4
        description = 'Ambush 3rd and 4th enemy with melee dmg.'

        @staticmethod
        def trigger_condition(owner: Character | Monster, data: Data) -> int:
            return index_trigger(owner, 4)
        
        target_with_effect = {
            'self' : 'attack',
            'monster_3:' : MeleeDamage
        }

    skillList = [B_Assult, B_BasicAttack, B_Revenge, B_Ambush]

class Cinnamon(Character):
    name = 'Cinnamon'
    icon = 'C'
    HP = 9
    key = 'c'
    speed = 3
    command = "(C)innamon"

    skillList = []

    def __init__(self):
        super().__init__(self.name, self.icon, self.HP, self.speed, self.key, self.command, self.skillList)

class Dahlia(Character):
    name = 'Dahlia'
    icon = 'D'
    HP = 7
    key = 'd'
    speed = 1
    command = "(D)ahlia"

    skillList = []

    def __init__(self):
        super().__init__(self.name, self.icon, self.HP, self.speed, self.key, self.command, self.skillList)

