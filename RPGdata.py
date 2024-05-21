from typing import Literal, Callable
from RPGclass import Event, Monster, Character

#Command의 뒤에 dataMethod와 필요한 매개변수를 붙여, key 입력 시 시행한다.
class SystemCommand():
    string : str
    key : str
    testMethod : Callable[[],str|tuple]
    hascommand : bool = True
    
    def __init__(self, string:str, key:str, testMethod:Callable|None = None):
        self.string = string 
        self.key = key
        self.testMethod = testMethod

    def get_command(self):
        if self.hascommand and self.string != None:
            return self.key, self.string
        else:
            return None
        
    def get_key(self):
        return self.key
        
    def run_method(self, data:'Data'):
        return self.testMethod(data)

class Data:
    monsters : list[Monster] = []
    players : list[Character] = []
    eventList : list[Event] = []
    commandList : dict[str, str] = {}
    testCommands : list[SystemCommand] = []
    isTest : bool = False
    isDialogOn : bool = True
    isBattlefieldOn : bool = True
    mode : Literal["select", "solve"]

    testplayer : Character
    
    def __init__(self):
        self.mode = "select"
        self.testplayer = Character("test player", "@", 30)
        self.testplayer.setVoice()
        #character instance 하나를 testplayer에 저장한다. 디버그용.
        self.generate_testCommands()
    
    def generate_testCommands(self):
        test_inputMessage = SystemCommand("(I)nput", 'i', lambda data: data.writeMessage())
        test_voiceChat = SystemCommand("(V)oice", 'v', lambda data: data.voiceChat(data.testplayer, "뭐라카노?", "_-^-."))
        test_add_player = SystemCommand("(P)layer add", 'p', lambda data: data.add_player(name=f"player {len(data.players) + 1}", icon="A", HP=20))
        test_delete_player = SystemCommand("(R)id player", 'r', lambda data: data.delete_player(len(data.players) - 1))
        test_add_monster = SystemCommand("(M)onster add", 'm', lambda data: data.add_monster(f"monster {len(data.monsters) + 1}", "M", 10))
        test_kill_monster = SystemCommand("(K)ill monster", 'k', lambda data: data.kill_monster(len(data.monsters) - 1))
        test_add_event = SystemCommand("(E)vent add", 'e', lambda data: data.add_sampleEvent())
        test_clear_event = SystemCommand("(F)inish event", 'f', lambda data: data.clear_event())
        self.testCommands = [
            test_inputMessage,
            test_voiceChat,
            test_add_player,
            test_delete_player,
            test_add_monster,
            test_kill_monster,
            test_add_event,
            test_clear_event
        ]

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
        
    def make_commandList(self):
        #asdf
        commandList = {}
        for entity in self.testCommands + self.players + self.monsters:
            #single command for single entity
            command : tuple|None = entity.get_command()
            if type(command) == tuple and command[0] != None:
                commandList.update(dict([command]))
            self.commandList = commandList

    def run_command(self, key:str, mode:str) -> str|tuple|None:
        self.mode = mode
        for entity in self.players + self.monsters + self.testCommands:
            if entity.get_key() == key:
                if isinstance(entity, Character):
                    if entity.index == 0:
                        entity.index = self.playerIndexCheck()
                    elif entity.index in [1, 2, 3, 4]:
                        entity.index = 0
                        self.playerIndexCheck()
                    self.make_eventList()
                    return None

                elif isinstance(entity, SystemCommand):
                    event = entity.run_method(self)
                    return event
        return "No such key!\n"

    def make_eventList(self):
        for player in self.players:
            index = player.index
            event = player.get_event(self)
            time = 0
            if event != None and event.speed >= 0:
                self.eventList.insert(index, event)
                time += event.speed
                #time 속성은 여기서만 부여
                event.time = time
    
        for monster in self.monsters:
            event = monster.get_event(self)
            time = 0
            if event.speed > 0:
                time += event.speed
                for index, event in enumerate(self.eventList):
                    if event.time > time:
                        self.eventList.insert(index, event)
            elif event.speed == 0:
                self.eventList.append(event)

    def process_eventList(self):
        self.mode = "process"

    def writeMessage(self, text:str='default'):
        if text == 'default':
            return "nvoierhaoivhgoiewjhaoivghoiheiowhasdfafdadsasdfawecfewacfecwaeoivhoi하다니wjovig\n"
        elif type(text) == str:
            return text

    def voiceChat(self, character: Character, text:str, accent:str):
        return "chat", character.voice.speakgen(text, accent)

    #아군 추가
    def add_player(self, character:Character|None=None, name:str='test player', icon:str='@', HP:int=10, voice:dict|Literal["silent"]|None=None):
        #템플릿이 있으면 복사
        if character != None:
            new_creature = character
        #아니면 새로 생성
        else:
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
        self.testplayer = new_creature
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
            text = f"p \'{self.players[-1].name}\' was deleted.\n"
            self.players.pop(index_in_players)
            return text
        except IndexError:
            return "no such player index in players\n"
        
    #샘플 이벤트 추가. 기본적으로 맨 뒤에, index가 주어지면 eventList[index]에 추가.
    def add_sampleEvent(self, index:int|None=None):
        new_event = Event(self.testplayer, {'monster_1':'damage'}, self)
        if index == None:
            self.eventList.append(new_event)
        elif type(index) == int:
            self.eventList.insert(index, new_event)
        return "event \'test\' added\n"

    #이벤트 삭제. 기본적으로 맨 아래.
    def clear_event(self, index:int= -1):

        keep = True
#        while keep == True:
#            for effect in self.eventList[index].origins:
#                keep = effect.execute(self)
#        if keep == True:
#            for effect in self.eventList[index].targets:
#                keep = effect.execute(self)
        try:
            self.eventList.pop(index)
            return "last event cleared\n"
        except IndexError:
            return "No such event index in eventList\n"