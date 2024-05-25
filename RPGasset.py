from RPGclass import Character, Event, Monster
from RPGdata import Data

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

#Character 추가
class A_Protect(Event):
    @staticmethod
    def trigger_condition(owner: Character | Monster, data: Data) -> int:
        return index_trigger(owner, 1)
   
    target_with_effect = {
        'self' : 'shield'
    }

class A_SingleHit(Event):
    @staticmethod
    def trigger_condition(owner: Character | Monster, data: Data) -> int:
        return index_trigger(owner, 2)

    target_with_effect = {
        'self' : 'attack',
        'monster_1' : 'damage'
    }

class A_MultiHit(Event):
    @staticmethod
    def trigger_condition(owner: Character | Monster, data: Data) -> int:
        return index_trigger(owner, 3)

    target_with_effect = {
        'self' : 'attack',
        'monster_' : 'damage'
    }

class A_Backup(Event):
    @staticmethod
    def trigger_condition(owner: Character | Monster, data: Data) -> int:
        return index_trigger(owner, 4)

    target_with_effect = {
        'self' : 'attack',
        'monster_-1' : 'damage'
    }

andrew = Character(
    name = 'Andrew',
    icon = 'A',
    HP = 12,
    key = 'a',
    speed = 4,
    command = "(A)ndrew",
    skillList = [A_Protect, A_SingleHit, A_MultiHit, A_Backup]
)

brian = Character(
    name = 'Brian',
    icon = 'B',
    HP = 10,
    key = 'b',
    speed = 2,
    command = "(B)rian"
)

cinnamon = Character(
    name = 'Cinnamon',
    icon = 'C',
    HP = 9,
    key = 'c',
    speed = 3,
    command = "(C)innamon"
)

dahlia = Character(
    name = 'Dahlia',
    icon = 'D',
    HP = 7,
    key = 'd',
    speed = 1,
    command = "(D)ahlia"
)
