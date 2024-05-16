import RichUI
from RPGclass import character, monster, Data
from rich.live import Live
from typing import Literal

WIDTH = 120
HEIGHT = 30

class Main:
    #추상적 클래스 선언. console, data 불러오기.
    testplayer : character
    ui : RichUI.UI
    data : Data
        
    def __init__(self):
        self.ui = RichUI.console
        self.data = Data()

        self.add_creature("test player", "@", type='character')
        self.testplayer = self.data.players[0]


    def add_creature(self, name:str, icon:str, voice: dict|None = None, type:Literal["character", "monster"]="character"):
        #아군 추가
        if type == "character":
            new_creature = character(name, icon)
            if voice == dict:
                new_creature.setVoice(**voice)
            else:
                new_creature.setVoice()
            self.data.players.append(new_creature)
        
        #적군 추가
        elif type == "monster":
            new_creature = monster(name, icon)
            self.data.monsters.append(new_creature)

#class Dialog:
#    #아직 안 씀
#   def initwrite(self):
#        self.narrator = character()
#        self.narrator.setVoice()
#        return self.narrator.voice.speakgen("player set",
#                                            "------.---")

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
            
            #return_event with function
            elif user_input == 'i':
                main.ui.dwrite(f"nvoierhaoivhgoiewjhaoivghoiheiowhoivhoi하다니wjovig\n")
            
            #yield_event with generator
            elif user_input == 'v':
                for char in (main.testplayer.voice.speakgen("뭐라카노?", "_-^-.")):
                    main.ui.dwrite(char)
                    updateUI() #refreshes with changed main.console.

            elif user_input == 'a':
                main.add_creature(f"player {len(main.data.players) + 1}", "A", type='character')
                main.ui.dwrite(f"Character {main.data.players[-1].name} was added.\n")

            elif user_input == 'm':
                main.add_creature(f"monster {len(main.data.monsters) + 1}", "M", type='monster')
                main.ui.dwrite(f"Monster {main.data.monsters[-1].name} was added.\n")

            #after event, refreshes with debugging print
            if user_input != None:
                input_counter += 1
                main.ui.twrite(main.data)
                main.ui.dwrite(f"{input_counter} updated\n")
                updateUI() #refreshes with changed main.console.
