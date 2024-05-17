import RichUI
from RPGclass import Character, Monster, Data, Event
from rich.live import Live
from typing import Literal

WIDTH = 120
HEIGHT = 30

class Main:
    #추상적 클래스 선언. console, data 불러오기.
    testplayer : Character
    ui : RichUI.UI
    data : Data
        
    def __init__(self):
        self.ui = RichUI.console
        self.data = Data()

        #처음에 player 하나를 추가한다. 디버그용.
        self.add_player("test player", "@")

        #character instance 하나를 Main.testplayer에 저장한다. 디버그용.
        self.testplayer = self.data.players[0]

    #아군 추가
    def add_player(self, name:str, icon:str, voice:dict|Literal["silent"]|None = None):
        #생성
        new_creature = Character(name, icon)
        #목소리 설정
        if voice == dict:
            new_creature.setVoice(**voice)
        elif voice == "silent":
            pass
        else:
            new_creature.setVoice()
        #index 설정
        new_creature.index = self.data.playerIndexCheck()
        #추가
        self.data.players.append(new_creature)
    
    #적군 추가
    def add_monster(self, name:str, icon:str):
        #생성
        new_creature = Monster(name, icon)
        #index 설정
        new_creature.index = len(self.data.monsters) + 1
        #추가
        self.data.monsters.append(new_creature)

    #아군 삭제. 가장 왼쪽이 기본값.
    def delete_player(self, index_in_players:int= -1):
        try:
            self.data.players.pop(index_in_players)
        except IndexError:
            self.ui.dwrite("no such player index in players\n")

    #적군 삭제. 가장 오른쪽이 기본값.
    def kill_monster(self, index_in_monsters:int= -1):
        try:
            self.data.monsters.pop(index_in_monsters)
        except IndexError:
            self.ui.dwrite("no such monster index in monsters\n")

    #이벤트 추가. 기본적으로 맨 뒤에, index가 주어지면 eventList[index]에 추가.
    def add_event(self, typ:str="test", index:int | None = None):
        new_event = Event()
        if index == None:
            self.data.eventList.append(new_event)
        else:
            self.data.eventList.insert(index, new_event)
        self.data.eventIndexRefresh()

    #이벤트 삭제. 기본적으로 맨 아래.
    def clear_event(self, index:int= -1):
        try:
            self.data.eventList.pop(index)
        except IndexError:
            self.ui.dwrite("No such event index in eventList\n")

if __name__ == "__main__":
    main = Main()

    #Makes Layout() from present main.ui
    def layoutgen():
        return main.ui.layoutgen()

    with Live(layoutgen(), auto_refresh=False) as live:
        #Live(Layout()), arg) as live:
        #    ...
        #    updateUI()
        #    ...
        #    updateUI()
        #처럼 동작.
        
        #앞으로 화면 갱신 시 이걸 쓸 거임.
        def updateUI():
            live.update(layoutgen(), refresh=True)
        #이렇게.
        updateUI()

        input_counter = 0
        while True:
            user_input = input("Press your input")
            
            if user_input == 'q':
                break
            
            #(I)nput
            elif user_input == 'i':
                main.ui.dwrite(f"nvoierhaoivhgoiewjhaoivghoiheiowhoivhoi하다니wjovig\n")
            
            #(V)oice
            elif user_input == 'v':
                for char in (main.testplayer.voice.speakgen("뭐라카노?", "_-^-.")):
                    main.ui.dwrite(char)
                    #현재 dialog 내용으로 새 layout을 출력한다.
                    updateUI()

            #(P)layer add
            elif user_input == 'p':
                #player를 data에 추가한다.
                main.add_player(f"player {len(main.data.players) + 1}", "A")
                #dialog를 갱신한다.
                main.ui.dwrite(f"Character \'{main.data.players[-1].name}\' was added.\n")

            #(M)onster add
            elif user_input == 'm':
                #Monster를 data에 추가한다.
                main.add_monster(f"monster {len(main.data.monsters) + 1}", "M")
                #dialog를 갱신한다.
                main.ui.dwrite(f"Monster \'{main.data.monsters[-1].name}\' was added.\n")

            #(D)ead player
            elif user_input == 'd':
                try:
                    main.ui.dwrite(f"player \'{main.data.players[-1].name}\' was deleted.\n")
                    main.delete_player(len(main.data.players) - 1)
                except IndexError:
                    main.ui.dwrite("No more players to delete!\n")

            #(K)ill monster
            elif user_input == 'k':
                try:
                    main.ui.dwrite(f"monster \'{main.data.monsters[-1].name}\' was deleted.\n")
                    main.kill_monster(len(main.data.monsters) - 1)
                except IndexError:
                    main.ui.dwrite("No more monsters to delete!\n")

            #(E)vent add
            elif user_input == 'e':
                main.add_event(typ="test")
                main.ui.dwrite(f"event \'test\' added\n")

            #(C)lear event
            elif user_input == 'c':
                try:
                    main.ui.dwrite("trying to clear last event...\n")
                    main.clear_event()
                except IndexError:
                    main.ui.dwrite("no such event!\n")


            elif not user_input.isascii():
                main.ui.dwrite("Not ASCII! (한/영 키 확인)\n")

            #after event, refreshes with debugging print
            if user_input != None:
                input_counter += 1
                #battlefield을 갱신한다.
                main.ui.bwrite(main.data)
                #dialog에 디버그 메시지를 출력한다.
                main.ui.dwrite(f"{input_counter} updated\n")
                #commandbox를 갱신한다.
                main.ui.cwrite("Command you can use: ")
                #현재 battlefield, dialog, messagebox의 내용으로 새 layout을 출력한다.
                updateUI()
