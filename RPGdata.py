from typing import Literal, Callable
from RPGclass import Event, Monster, Character, Buff

#Command의 뒤에 dataMethod와 필요한 매개변수를 lambda로 붙여, key 입력 시 시행한다.
class SystemCommand():
    string : str
    key : str
    testMethod : Callable[[],str|tuple]
    
    def __init__(self, string:str, key:str, testMethod:Callable|None = None, mode:str|None=None):
        self.string = string 
        self.key = key
        self.testMethod = testMethod
        self.when_active = mode

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
    raw_dialog : str = ""

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
        status = {}
        #Only added in here
        dummy = True

        def __init__(self, index=0):
            self.index = index
            self.available_events = []
    
    def __init__(self):
        self.mode = "select"
        #character instance 하나를 testplayer에 저장한다. 디버그용.
        self.testplayer = Character("test player", "@", 30)
        self.testplayer.setVoice({
            'high': 740,
            'middle': 455,
            'low': 350,
            'sec': 0.11
        })
        self.buff = Buff(self)

        self.fill_dummy()
        self.generate_testCommands()

    def generate_testCommands(self):
        test_inputMessage = SystemCommand("(L)og", 'l', lambda data: data.add_log('test'))
        test_voiceChat = SystemCommand("(V)oice", 'v', lambda data: data.voiceChat(data.testplayer, "뭐라카노?", "_-^-."))
        test_open_info = SystemCommand("(I)nfo", 'i', lambda data: data.open_emptyinfo(), 'battlefield')
        test_close_info = SystemCommand("(I)nfo close", 'i', lambda data:data.close_info(), 'info')
        test_add_player = SystemCommand("(P)layer add", 'p', lambda data: data.add_player(name=f"player {len(data.players) + 1}", icon="A", HP=20))
        test_delete_player = SystemCommand("(R)id player", 'r', lambda data: data.delete_player(len(data.players) - 1))
        test_add_monster = SystemCommand("(M)onster add", 'm', lambda data: data.add_monster(name=f"dummymon", icon="M", HP=10))
        test_kill_monster = SystemCommand("(K)ill monster", 'k', lambda data: data.kill_monster(len(data.monsters) - 1))
        test_add_event = SystemCommand("(E)vent add", 'e', lambda data: data.add_sampleEvent())
        test_clear_event = SystemCommand("(F)inish event", 'f', lambda data: data.clear_event())
        test_proceed_turn = SystemCommand("(T)urn proceed", 't', lambda data: data.proceed_turn())
        self.testCommands = [
            test_inputMessage,
            test_voiceChat,
            test_open_info,
            test_close_info,
            test_add_player,
            test_delete_player,
            test_add_monster,
            test_kill_monster,
            test_add_event,
            test_clear_event,
            test_proceed_turn
        ]
    
    def fill_dummy(self, given_index=None):
        '''players의 index 오류를 수정하고, 빈 자리는 dummy로 채운다. index가 주어지면 index에만 채운다.'''
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

    def clear_dummy(self):
        for dummy in [player for player in self.players if hasattr(player, 'dummy')]:
            self.players.remove(dummy)
            del(dummy)
    
    def playerIndexUpdate(self, new_player:'Character'):
        '''남아있는 자리 중 가장 앞쪽을 반환한다. 없으면 0을 반환한다.'''
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
        '''monsters 중 HP가 0인 개체를 제거한다. 아니면 index = 1부터 재배열한다.'''
        #HP 0 제거
        for monster in list(filter(lambda mon : mon.HP == 0, self.monsters)):
            self.monsters.remove(monster)
            del(monster)
        #monsters 순서대로 index 재부여
        new_index = 0
        for monster in self.monsters:
            monster.index = new_index
            new_index += 1
        
    def make_commandList(self, main_mode:str):
        '''commandbox 갱신 시 실행된다. get_command의 결과를 commandList에 추가한다.'''
        commandList = {}
        for entity in self.testCommands + self.players + self.monsters:
            if hasattr(entity, 'when_active') and entity.when_active not in [main_mode, None]:
                continue
            #single command for single entity
            command : tuple|None = entity.get_command(self.mode)
            if type(command) == tuple and command[0] != None:
                commandList.update(dict([command]))
            self.commandList = commandList
    
    #key 입력 시 실행된다.
    def run_command(self, key:str, main_mode:str) -> tuple|str|None:
        for entity in self.players + self.monsters + self.testCommands:
            if hasattr(entity, 'when_active') and entity.when_active not in [main_mode, None]:
                continue
            if entity.get_key() == key:
                #Creature 선택 시
                if isinstance(entity, Character):
                    if entity.index == 0:
                        self.playerIndexUpdate(entity)
                    elif entity.index in [1, 2, 3, 4]:
                        entity.index = 0
                        self.fill_dummy(entity.index)
                    self.make_eventList()
                    return None
                #SystemCommand 선택 시
                elif isinstance(entity, SystemCommand):
                    output = entity.run_method(self)
                    return output
        #일치하는 key가 없어 return문을 시행하지 못하면:
        self.add_log("No such key!\n")

    #data가 변할 시 불러와져야 한다.
    def make_eventList(self):
        '''players와 monsters에서 get_event를 수행해, event에 time을 부여하고 eventList에 추가한다.'''
        playereventList :list[Event] = []
        for player in self.players:
            if player.index in [1, 2, 3, 4]:
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
        self.buff.refresh_buff(self)
        if self.buff.effects != []:
            eventlist.append(self.buff)
        self.eventList = eventlist

    def proceed_turn(self):
        survivors = [player for player in self.players if player.has_command(self.mode)]
        if self.mode == 'select' and set(player.index for player in survivors) != {x + 1 for x in range(min(len(survivors), 4))}:
            self.add_log("Select all character.\n")
            return None

        self.mode = "process"
        if self.buff in self.eventList:
            self.eventList.remove(self.buff) 
        if self.eventList == []:
            self.monsterIndexRefresh()
            self.clear_dummy()
            for player in self.players:
                player.index = 0
                player.check_status_turn()
            self.fill_dummy()
            self.make_eventList()
            self.mode = 'select'
            self.add_log("turn ended\n")
        else:
            log = self.clear_event(0)
            for event in self.eventList:
                if event.effects == [] or (event.origin != None and event.origin.isDead()):
                    self.eventList.remove(event)
                    del(event)
            self.buff.refresh_buff(self)
            if self.buff not in self.eventList and self.buff.effects != []:
                self.eventList.append(self.buff)
            if log is str:
                self.add_log(log)

    ### debug ##################################################################
    def add_log(self, text:str):
        if text == 'test':
            self.raw_dialog += "nvoierhaoivhgoiewjhaoivghoiheiowhasdfafdadsasdfawecfewacfecwaeoivhoi하다니wjovig\n"
        else:
            self.raw_dialog += text

    def voiceChat(self, character: Character, text:str, accent:str):
        if hasattr(character, 'voice'):
            gen = character.voice.speakgen(text, accent)
            return "chat", gen
        else:
            self.add_log(f"{character.name} does not have a voice.\n")

    def open_emptyinfo(self):
        emptyinfo = "An empty info screen for debugging."
        self.info = emptyinfo
        return 'info'
    
    def close_info(self):
        return 'battlefield'

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

        self.add_log(f"Character \'{new_creature.name}\' was added.\n")

    #적군 추가
    def add_monster(self, monster:Monster|None=None, name:str='monster', icon:str='M', HP:int=10):
        #템플릿이 있으면 복사
        if monster != None:
            new_creature = monster
        #아니면 새로 생성
        else:
            new_creature = Monster(name, icon, HP)
            self.testplayer = new_creature
        
        #index 설정
        new_creature.index = len(self.monsters) + 1
        Monster.num += 1
        #추가
        counter = 1
        name_exists = any(new_creature.name in monster.name for monster in self.monsters)
        while name_exists:
            new_creature.name = f"{new_creature.name} {counter}"
            name_exists = any(new_creature.name in monster.name for monster in self.monsters)
            counter += 1
        self.monsters.append(new_creature)
        self.make_eventList()
        self.add_log(f"Monster \'{new_creature.name}\' was added.\n")

    #적군 삭제. 가장 오른쪽이 기본값.
    def kill_monster(self, index_in_monsters:int= -1):
        try:
            monster = self.monsters[index_in_monsters]
            text = f"monster \'{monster.name}\' was deleted.\n"
            self.monsters.pop(index_in_monsters)
            del(monster)
            self.make_eventList()
            self.add_log(text)
        except IndexError:
            self.add_log("no such monster index in monsters\n")

    #아군 삭제. 가장 왼쪽이 기본값.
    def delete_player(self, index_in_players:int= -1):
        try:
            player = self.players[index_in_players]
            text = f"p \'{player.name}\' was deleted.\n"
            self.players.pop(index_in_players)
            self.fill_dummy()
            del(player)
            self.make_eventList()
            self.add_log(text)
        except IndexError:
            self.add_log("no such player index in players\n")
        
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
        self.add_log("event \'test\' added\n")

    #이벤트 삭제. 기본적으로 맨 아래.
    def clear_event(self, index:int= -1):

        keep = True
#        while keep == True:
#            for effect in self.eventList[index].origins:
#                keep = effect.execute(self)
#        if keep == True:
        try:
            log = self.eventList[index].execute_self(self)
            self.eventList.pop(index)
            self.add_log(log + "last event cleared\n")
        except IndexError:
            self.add_log("No such event index in eventList\n")