import os, keyboard
from RPGclass import Character, Monster, Data, Event
from RichUI import UI
from rich.live import Live
from typing import Literal

terminalSize = os.get_terminal_size()
WIDTH = terminalSize.columns
HEIGHT = terminalSize.lines

class Main:
    #추상적 클래스 선언. console, data 불러오기.
    testplayer : Character
    ui : UI
    data : Data
        
    def __init__(self):
        self.ui = UI(WIDTH, HEIGHT)
        self.data = Data()

        #처음에 player 하나를 추가한다. 디버그용.
        self.data.add_player("test player", "@", 30)

        #character instance 하나를 Main.testplayer에 저장한다. 디버그용.
        self.data.testplayer = self.data.players[0]

    def reset_terminal_size(self):
        global WIDTH, HEIGHT
        terminalSize = os.get_terminal_size()
        WIDTH = terminalSize.columns
        HEIGHT = terminalSize.lines
        self.ui.resize(WIDTH, HEIGHT)

    def actionCaller(self, user_input:str):
        try:
            output = self.data.choiceList[user_input].do()
            if isinstance(output, str):
                return {'dmessage' : output}
            elif isinstance(output, tuple) and len(output) > 0 and output[0] == 'chat':
                return dict([output])
        except KeyError:
            return None
        
#종료 후 입력 버퍼 초기화.
def clear_terminal_buffer():
    import os
    if os.name == 'nt':
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getch()
    else:
        import termios
        import sys
        import tty
        termios.tcflush(sys.stdin, termios.TCIOFLUSH)

if __name__ == "__main__":
    main = Main()
    #아직 만드는 중
    main.data.isTest = True

    #Makes Layout() from present main.ui
    def layoutgen():
        return main.ui.layoutgen()

    with Live(layoutgen(), console=main.ui, auto_refresh=False) as live:
        #Live(Layout()), arg) as live:
        #    ...
        #    updateUI()
        #    ...
        #    updateUI()
        #처럼 동작.
        
        #앞으로 화면 갱신 시 이걸 쓸 거임.
        def updateUI():
            #terminal 크기 갱신하고,
            main.reset_terminal_size()
            #새 layout 생성해서 깔기
            live.update(layoutgen(), refresh=True)
        #이렇게.
        updateUI()

        input_counter = 0
        while True:
            #키보드 입력 시까지 일시정지
            key_event = keyboard.read_event()
            #키보드 'DOWN' 시 입력 받음
            if key_event.event_type == 'down':
                user_input = key_event.name
            #아니면 key_event 다시 받기
            else:
                continue
            
            #항상 q로 종료
            if user_input == 'q':
                break
            elif user_input == '`':
                while True:
                    resume = keyboard.read_event()
                    if resume.event_type == 'down' and resume.name == '`':
                        break

            #한/영 키 확인
            elif not user_input.isascii():
                main.ui.dwrite("Not ASCII! (한/영 키 확인)\n")

            else:
                output : dict|None = main.actionCaller(user_input)
                #{'결과 종류':'결과값'}
                if type(output) == dict:
                    #일반 메시지
                    if 'dmessage' in output:
                        main.ui.dwrite(output.get('dmessage'))
                    #실시간 갱신 메시지
                    if 'chat' in output:
                        #char의 대상은 Generator로, sleep()이 걸려 있다.
                        for char in output.get('chat'):
                            main.ui.dwrite(char)
                            #한 글자마다 현재 dialog 내용으로 새 layout을 출력한다.
                            updateUI()

            #after event, refreshes with debugging print
            if user_input != None:
                input_counter += 1
                #battlefield을 갱신한다.
                main.ui.bwrite(main.data)
                #dialog에 디버그 메시지를 출력한다.
                main.ui.dwrite(f"{input_counter} updated\n")
                #commandbox를 갱신한다.
                main.data.make_choiceList()
                main.ui.cwrite(main.data.choiceList)
                #현재 battlefield, dialog, messagebox의 내용으로 새 layout을 출력한다.
                updateUI()
        
        #입력 버퍼 초기화 후 Live 종료.
        clear_terminal_buffer()
    #Live 끝
#main 끝
