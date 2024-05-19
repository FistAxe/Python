import voicefunc
from typing import Literal, List, Callable

class Choice:
    command : str
    string : str
    action : Callable
    fixedarg : tuple

    def __init__(self, string:str, dataMethod:Callable|None = None, *fixedarg, **fixedkwarg):
        self.action = dataMethod
        self.string = string
        self.fixedarg = fixedarg
        self.fixedkwarg = fixedkwarg

    def do(self, *arg, **kwarg):
        if callable(self.action):
            return self.action(*self.fixedarg, *arg, **self.fixedkwarg, **kwarg)

class Creature:
    def __init__(self, name:str, icon:str, HP:int, key:str=None):
        self.name = name
        self.icon = icon
        self.HP = self.max_HP = HP
        self.key = key
        self.hasChoice : bool = False

class Monster(Creature):
    index : int

    def __init__(self, name:str, icon:str, HP:int):
        super().__init__(name, icon, HP)

    def get_choice(self):
        if self.hasChoice == False:
            return None
        else:
            choice = Choice(f"Blank {self.name} choice")
            return choice


class Character(Creature):
    index : Literal[0, 1, 2, 3, 4]

    def __init__(self, name:str, icon:str, HP:int):
        self.index = 0
        super().__init__(name, icon, HP)
    
    def setVoice(self, high=740, middle=455, low=350, sec=0.13):
        self.voice = voicefunc.voice(high, middle, low, sec)

    def get_choice(self):
        if self.index in [1, 2, 3, 4]:
            choice = Choice(f"Blank {self.name} choice")
            choice.command = self.key
            return choice
        else:
            return None

#이벤트. 원인과 효과(들), 대상과 효과(들)을 가진다.
#[(원인 1, 효과 1), (원인 2, 효과 2) ... ] -> [(대상 1, 효과 1), (대상 2, 효과 2) ... ]
class Event:
    #대상과 그 효과 
    class SingleEffect:
        #효과
        class Effect:
            #All private var. Access by Effect.get_method().
            _typ : str
            _icon : str
            _value : str
            _color : str

            def __init__(self, effect_type, value:int|None=None):
                if effect_type == 'test':
                    self._typ = 'test'
                    self._icon = ':gear:'
                    self._color = 'bg_test_yellow'
                if effect_type == 'damage':
                    self._typ = 'damage'
                    self._icon = ':drop_of_blood:'
                    self._value = "[b red]-7[/b red]"
                    self._color = 'bg_damage_red'
                if effect_type == 'attack':
                    self._typ = 'attack'
                    self._icon = '⚔'
                    self._color = 'bg_attack_yellow'

        #public
        target : Character | str
        #private
        _effect : Effect

        def __init__(self, target, effect_type):
            self.target = target
            self._effect = self.Effect(effect_type)

        def get_Icon(self):
            try:
                return self._effect._icon
            except:
                return "X"

        def get_content(self):
            try:
                return self._effect._value
            except:
                return None
            
        def get_color(self):
            try:
                return self._effect._color
            except:
                return None

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
    choiceList : dict[str, Choice] = {}
    isTest : bool = False
    isDialogOn : bool = True
    isBattlefieldOn : bool = True

    testplayer : Character
    
    def __init__(self):
        event = Event(
            {'player':'test'},
            {'monster':'test'}
        )
        self.eventList.append(event)
    
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
        
    def make_choiceList(self):
        #전역 행동 확인
        def check_global():
            choiceList = {}
            #디버그용
            if self.isTest == True:
                if self.isDialogOn == True:
                    test_inputMessage = Choice("(I)nput", self.inputMessage)
                    test_voiceChat = Choice("(V)oice", self.voiceChat, self.testplayer, "뭐라카노?", "_-^-.")
                    choiceList.update(
                        {
                        'i' : test_inputMessage,
                        'v' : test_voiceChat
                        }
                    )
                if self.isBattlefieldOn == True:
                    test_add_player = Choice("(P)layer add", self.add_player, f"player {len(self.players) + 1}", "A", 20)
                    test_delete_player = Choice("(D)elete player", self.delete_player, len(self.players) - 1)
                    test_add_monster = Choice("(M)onster add", self.add_monster, f"monster {len(self.monsters) + 1}", "M", 10)
                    test_kill_monster = Choice("(K)ill monster", self.kill_monster, len(self.monsters) - 1)
                    test_add_event = Choice("(E)vent add", self.add_event, typ="test")
                    test_clear_event = Choice("(C)lear event", self.clear_event)

                    choiceList.update(
                        {
                        "p" : test_add_player,
                        "m" : test_add_monster,
                        "d" : test_delete_player,
                        "k" : test_kill_monster,
                        "e" : test_add_event,
                        "c" : test_clear_event
                        }
                    )
            return choiceList
        
        #아군 행동 확인
        def check_player():
            choiceList = {}
            for player in self.players:
                #single choice for single player
                choice : Choice|None = player.get_choice()
                if choice != None and choice.command != None:
                    choiceList.update({choice.command : choice})
            return choiceList
        
        #적군 행동 확인 (보통 거의 없음)
        def check_monster():
            choiceList = {}
            for monster in self.monsters:
                #single choice for single player
                choice : Choice|None = monster.get_choice()
                if choice != None:
                    choice.command = 'o'
                    choiceList.update({choice.command : choice})
            return choiceList
        
        #main
        choiceList = {}
        choiceList.update(check_global())
        choiceList.update(check_player())
        choiceList.update(check_monster())
        self.choiceList = choiceList

    def inputMessage(self):
        return "nvoierhaoivhgoiewjhaoivghoiheiowhoivhoi하다니wjovig\n"

    def voiceChat(self, character: Character, text:str, accent:str):
        return "chat", character.voice.speakgen(text, accent)


    #아군 추가
    def add_player(self, name:str, icon:str, HP:int, voice:dict|Literal["silent"]|None = None):
        #생성
        new_creature = Character(name, icon, HP)
        #목소리 설정
        if voice == dict:
            new_creature.setVoice(**voice)
        elif voice == "silent":
            pass
        else:
            new_creature.setVoice()
        #index 설정
        new_creature.index = self.playerIndexCheck()
        #추가
        self.players.append(new_creature)
        return f"Character \'{self.players[-1].name}\' was added.\n"

    #적군 추가
    def add_monster(self, name:str, icon:str, HP:int):
        #생성
        new_creature = Monster(name, icon, HP)
        #index 설정
        new_creature.index = len(self.monsters) + 1
        #추가
        self.monsters.append(new_creature)
        return f"Monster \'{self.monsters[-1].name}\' was added.\n"

    #적군 삭제. 가장 오른쪽이 기본값.
    def kill_monster(self, index_in_monsters:int= -1):
        try:
            text = f"monster \'{self.monsters[-1].name}\' was deleted.\n"
            self.monsters.pop(index_in_monsters)
            return text
        except IndexError:
            return "no such monster index in monsters\n"

    #아군 삭제. 가장 왼쪽이 기본값.
    def delete_player(self, index_in_players:int= -1):
        try:
            text = f"monster \'{self.players[-1].name}\' was deleted.\n"
            self.players.pop(index_in_players)
            return text
        except IndexError:
            return "no such player index in players\n"
        
    #이벤트 추가. 기본적으로 맨 뒤에, index가 주어지면 eventList[index]에 추가.
    def add_event(self, typ:str="test", index:int | None = None):
        new_event = None
        if typ == "test":
            new_event = Event(
                {'test player':'attack'
                 },
                {'monster':'damage'}
            )

        if new_event != None:
            if index == None:
                self.eventList.append(new_event)
            else:
                self.eventList.insert(index, new_event)

        return f"event \'test\' added\n"

    #이벤트 삭제. 기본적으로 맨 아래.
    def clear_event(self, index:int= -1):
        try:
            self.eventList.pop(index)
            return "last event cleared\n"
        except IndexError:
            return "No such event index in eventList\n"
        
