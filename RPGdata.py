from typing import Literal, Callable
from RPGclass import Event, Monster, Character

#Command의 뒤에 dataMethod와 필요한 매개변수를 붙여, key 입력 시 시행한다.
class SystemCommand():
    string : str
    key : str
    testMethod : Callable[[],str|tuple]
    
    def __init__(self, string:str, key:str, testMethod:Callable|None = None):
        self.string = string 
        self.key = key
        self.testMethod = testMethod

    def has_command(self, mode:str):
        return True

    def get_command(self, mode:str):
        if self.has_command(mode) and self.string != None:
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
    mode : Literal["select", "process"]

    testplayer : Character

    class DummyCharacter(Character):
        name="Dummy player"
        icon=" "
        HP=1
        max_HP = 1
        voice=None
        key=None
        hascommand = False
        command = None
        status = " "
        #Only added in here
        dummy = True

        def __init__(self, index=0):
            self.index = index
            self.available_events = []
    
    def __init__(self):
        self.mode = "select"
        #character instance 하나를 testplayer에 저장한다. 디버그용.
        self.testplayer = Character("test player", "@", 30)
        self.testplayer.setVoice()

        self.fill_dummy()
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
        test_proceed_turn = SystemCommand("(T)urn proceed", 't', lambda data: data.proceed_turn())
        self.testCommands = [
            test_inputMessage,
            test_voiceChat,
            test_add_player,
            test_delete_player,
            test_add_monster,
            test_kill_monster,
            test_add_event,
            test_clear_event,
            test_proceed_turn
        ]

    #Event의 수
    def event_num(self):
        return len(self.eventList)
    
    #players의 index 오류를 수정하고, 빈 자리는 dummy로 채운다. index의 빈 자리를 앞쪽부터 반환한다.
    def fill_dummy(self, given_index=None):
        indexlist = [1, 2, 3, 4]
        for player in self.players:
            if not hasattr(player, "index"):
                player.index = 0

        #수정. given index에 dummy 추가.
        if given_index != None and given_index in indexlist:
            self.players.append(self.DummyCharacter(given_index))
            
        #초기화. index가 1,2,3,4 중 하나라면 그 자리는 차 있다.
        else:
            existing_indexes = {player.index for player in self.players}
            for index in indexlist:
                if index not in existing_indexes:
                    self.players.append(self.DummyCharacter(index))
    
    def playerIndexUpdate(self, new_player:'Character'):
        #남아있는 자리 중 가장 앞쪽을 반환한다. 없으면 0을 반환한다.
        real_indexes = {player.index for player in self.players if not hasattr(player, 'dummy')}
        new_player.index = 0
        for index in [1, 2, 3, 4]:
            if index not in real_indexes:
                new_player.index = index
                break
        
        for i, instance in enumerate(self.players):
            if instance.index == new_player.index and hasattr(instance, 'dummy'):
                self.players.pop(i)
                del(instance)

    def monsterIndexRefresh(self):
        new_index = 0
        for monster in self.monsters:
            if monster.HP == 0:
                self.monsters.remove(monster)
                del(monster)
            else:
                new_index += 1
                monster.index = new_index
        
    #commandbox 갱신 시 실행된다.
    def make_commandList(self):
        #asdf
        commandList = {}
        for entity in self.testCommands + self.players + self.monsters:
            #single command for single entity
            command : tuple|None = entity.get_command(self.mode)
            if type(command) == tuple and command[0] != None:
                commandList.update(dict([command]))
            self.commandList = commandList
    
    #key 입력 시 실행된다.
    def run_command(self, key:str, mode:str) -> str|tuple|None:
        for entity in self.players + self.monsters + self.testCommands:
            if entity.get_key() == key:
                if isinstance(entity, Character):
                    if entity.index == 0:
                        self.playerIndexUpdate(entity)
                    elif entity.index in [1, 2, 3, 4]:
                        entity.index = 0
                        self.fill_dummy(entity.index)
                    self.make_eventList()
                    return None

                elif isinstance(entity, SystemCommand):
                    output = entity.run_method(self)
                    return output
        return "No such key!\n"

    #data가 변할 시 불러와져야 한다.
    def make_eventList(self):
        playereventList = []
        for player in self.players:
            index = player.index
            event = player.get_event(self)
            time = 0
            if event != None and event.speed >= 0:
                playereventList.insert(index, event)
                time += event.speed
                #time 속성은 여기서만 부여
                event.time = time
    
        monstereventlist = []
        for monster in self.monsters:
            event = monster.get_event(self)
            if event != None:
                event.time = event.speed
                monstereventlist.append(event)
        monstereventlist = sorted(monstereventlist, key=lambda event: event.time)
        for i in range(len(monstereventlist) - 1):
            monstereventlist[i + 1].time += monstereventlist[i].time

        eventlist = playereventList + monstereventlist
        eventlist = sorted(eventlist, key=lambda event: event.time)
        self.eventList = eventlist


    def proceed_turn(self):
        self.mode = "process"
        if self.eventList == []:
            self.monsterIndexRefresh()
            for player in self.players:
                player.index = 0
            self.fill_dummy()
            self.make_eventList()
            self.mode = 'select'
            return "turn ended\n"
        else:
            self.clear_event(0)

    def writeMessage(self, text:str='default'):
        if text == 'default':
            return "nvoierhaoivhgoiewjhaoivghoiheiowhasdfafdadsasdfawecfewacfecwaeoivhoi하다니wjovig\n"
        elif type(text) == str:
            return text

    def voiceChat(self, character: Character, text:str, accent:str):
        if hasattr(character, 'voice'):
            return "chat", character.voice.speakgen(text, accent)
        else:
            return f"{character.name} does not have a voice.\n"

    #아군 추가
    def add_player(self, character:Character|None=None, name:str='test player', icon:str='@', HP:int=10, voice:dict|Literal["silent"]|None=None):
        #템플릿이 있으면 복사
        if character != None:
            new_creature = character
        #아니면 새로 생성
        else:
            new_creature = Character(name, icon, HP)
            self.testplayer = new_creature

        #목소리 설정
        if voice == dict:
            new_creature.setVoice(**voice)
        elif voice == "silent":
            pass
        else:
            new_creature.setVoice()
        
        #추가
        self.players.append(new_creature)
        self.playerIndexUpdate(new_creature)
        self.make_eventList()

        return f"Character \'{new_creature.name}\' was added.\n"

    #적군 추가
    def add_monster(self, name:str, icon:str, HP:int):
        #생성
        new_creature = Monster(name, icon, HP)
        #index 설정
        new_creature.index = len(self.monsters) + 1
        Monster.num += 1
        #추가
        self.monsters.append(new_creature)
        self.make_eventList()
        return f"Monster \'{new_creature.name}_{Monster.num}\' was added.\n"

    #적군 삭제. 가장 오른쪽이 기본값.
    def kill_monster(self, index_in_monsters:int= -1):
        try:
            monster = self.monsters[index_in_monsters]
            text = f"monster \'{monster.name}\' was deleted.\n"
            self.monsters.pop(index_in_monsters)
            del(monster)
            self.make_eventList()
            return text
        except IndexError:
            return "no such monster index in monsters\n"

    #아군 삭제. 가장 왼쪽이 기본값.
    def delete_player(self, index_in_players:int= -1):
        try:
            player = self.players[index_in_players]
            text = f"p \'{player.name}\' was deleted.\n"
            self.players.pop(index_in_players)
            self.fill_dummy()
            del(player)
            self.make_eventList()
            return text
        except IndexError:
            return "no such player index in players\n"
        
    #샘플 이벤트 추가. 기본적으로 맨 뒤에, index가 주어지면 eventList[index]에 추가.
    def add_sampleEvent(self, index:int|None=None):
        new_event = Event(
            self.players[-1],
            self,
            {'self_' : 'attack',
             'monster_1' : 'damage'}
            )
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
        try:
            self.eventList[index].execute_self(self)
            self.eventList.pop(index)
            return "last event cleared\n"
        except IndexError:
            return "No such event index in eventList\n"