import voicefunc
import RichUI
from rich.live import Live

width = 1080
height = 720

class creature:
    pass

class monster(creature):
    pass

class character(creature):
    def __init__(self):
        pass
    
    def setVoice(self, high=740, middle=455, low=350, sec=0.13):
        self.voice = voicefunc.voice(high, middle, low, sec)

class Main:
    #추상적 클래스 선언. console 불러오기.
    player : character
    ui : RichUI.UI
        
    def __init__(self):
        self.ui = RichUI.console
        self.player = character()
        self.player.setVoice()

class Dialog:
    #아직 안 씀
    def initwrite(self):
        self.narrator = character()
        self.narrator.setVoice()
        return self.narrator.voice.speakgen("player set",
                                            "------.---")

if __name__ == "__main__":
    main = Main()

    with Live(RichUI.layoutgen(main.ui), auto_refresh=False) as live:
        live.update(RichUI.layoutgen(main.ui), refresh=True)
         #screen init

        input_counter = 0
        while True:
            user_input = input("adf")
            
            if user_input == 'q':
                break
            elif user_input == 'i':
                RichUI.dwrite(main.ui, f"nvoierhaoivhgoiewjhaoivghoiheiowhoivhoiwjovig\n")
            elif user_input == 'v':
                for char in (main.player.voice.speakgen("뭐라카노?", "_-^-.")):
                    RichUI.dwrite(main.ui, char)
                    live.update(RichUI.layoutgen(main.ui), refresh=True) #refreshes with changed main.console.

            if user_input != None:
                input_counter += 1
                RichUI.dwrite(main.ui, f"{input_counter} updated\n")
                live.update(RichUI.layoutgen(main.ui), refresh=True) #refreshes with changed main.console.
