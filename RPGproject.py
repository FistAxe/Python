import voicefunc
import RichUI
from rich.live import Live
from typing import List, Literal, Optional

width = 1080
height = 720

class creature:
    def __init__(self, name:str, icon:str):
        self.name = name
        self.icon = icon

class monster(creature):
    def __init__(self, name:str, icon:str):
        super().__init__(name, icon)

class character(creature):
    def __init__(self, name:str, icon:str):
        super().__init__(name, icon)
    
    def setVoice(self, high=740, middle=455, low=350, sec=0.13):
        self.voice = voicefunc.voice(high, middle, low, sec)

class BF_Table():
    row : int
    pass

class Main:
    #추상적 클래스 선언. console 불러오기.
    testplayer : character
    ui : RichUI.UI
    bf_table : BF_Table
    players : List[character]
    monsters : List[monster]
        
    def __init__(self):
        self.ui = RichUI.console
        self.players = []
        self.monsters = []
        self.add_creature("test player", "@", type='character')
        self.testplayer = self.players[0]

        self.bf_table = BF_Table()
        self.update_bf_table()

    def update_bf_table(self):
        self.bf_table.row = len(self.players) + len(self.monsters)

    def add_creature(self, name:str, icon:str, voice: dict|None = None, type:Literal["character", "monster"]="character"):
        if type == "character":
            new_creature = character(name, icon)
            if voice == dict:
                new_creature.setVoice(**voice)
            else:
                new_creature.setVoice()
            self.players.append(new_creature)
        elif type == "monster":
            new_creature = monster(name, icon)
            self.monsters.append(new_creature)

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
        
        def updateUI():
            live.update(layoutgen(), refresh=True)
        
        updateUI()
        print("initialted")
         #screen init

        input_counter = 0
        while True:
            user_input = input("Press your input")
            
            if user_input == 'q':
                break
            
            #return_event with function
            elif user_input == 'i':
                main.ui.dwrite(f"nvoierhaoivhgoiewjhaoivghoiheiowhoivhoiwjovig\n")
            
            #yield_event with generator
            elif user_input == 'v':
                for char in (main.testplayer.voice.speakgen("뭐라카노?", "_-^-.")):
                    main.ui.dwrite(char)
                    updateUI() #refreshes with changed main.console.

            elif user_input == 't':
                main.update_bf_table()
                main.ui.twrite(main.bf_table)

            #after event, refreshes with debugging print
            if user_input != None:
                input_counter += 1
                main.ui.dwrite(f"{input_counter} updated\n")
                updateUI() #refreshes with changed main.console.
