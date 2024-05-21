from RPGclass import Character, Event

# coefficient={'type1':'coeff1', 'type2':'coeff2', ... } : value에 수정되는 값. type의 값*coeff 만큼이 value에 더해진다.

#'self' : 자기 자신.
#'p_i : i번째 아군. i=0일 시 제일 앞.
#'m_i : i번째 적군. i=0일 시 제일 앞.
#'p_least_attr' : attr이 가장 적은 대상.
#'p_most_attr' : attr이 가장 큰 대상.

#"attack" : 공격. 방해 불가.
#"move_i" : 이벤트 종료 후 i만큼 이동.
#"move_to_i" : 이벤트 종료 후 i 위치로 이동.
#"focus_damage" : 집중. damage 이상 공격 받으면 방해 가능.
#"heal" : 회복.

#"damage" : 공격받음. 최종 value만큼 HP에 피해를 받는다.
#   value : int -> 특정 수치만큼.
#   value : melee -> value에 공격자의 물리 공격력 대입.


#melee = Event.Effect("damage", atk='*1')

#heal = Event.Effect(
#    {'least' : "heal_"}
#)

andrew = Character(
    name = 'Andrew',
    icon = 'A',
    HP = 12,
    key = 'a',
    command = "(A)ndrew"
)

brian = Character(
    name = 'Brian',
    icon = 'B',
    HP = 10,
    key = 'b',
    command = "(B)rian"
)

cinnamon = Character(
    name = 'Cinnamon',
    icon = 'C',
    HP = 9,
    key = 'c',
    command = "(C)innamon"
)

dahlia = Character(
    name = 'Dahlia',
    icon = 'D',
    HP = 7,
    key = 'd',
    command = "(D)ahlia"
)
