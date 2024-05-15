import curses
import sys

class Screen:
    def __init__(self, stdscr, x=120, y=25):
        if (x > curses.COLS) or (y > curses.LINES):
            raise Exception("Too Small Terminal Size")
        
        self.window = curses.newwin(y, x)
        self.window.keypad(True)
        self.window.clear()
        self.window.border()
        
        by = dy = y - 2
        bx = 60
        dx = x - bx - 2
        self.battleline = Battleline(self.window, bx, by, 1, 1)
        self.dialog = Dialog(self.window, dx, dy, (bx + 1), 1)
        self.window.refresh()

    def refresh(self):
        self.window.refresh()

    def getch(self):
        self.window.getch()

class Box:
    def __init__(self, window, width, height, x, y):
        self.window = window.subwin(height, width, y, x)
        self.window.refresh()

    def setName(self, name):
        coord = self.window.getbegyx()
        size = self.window.getmaxyx()
        self.overwrite(name, 0, 0)

    def write(self, text, x, y):
        self.window.addstr(y, x, text + "\n")
        self.window.refresh()

    def overwrite(self, text, x, y):
        for chr in text:
            self.window.addch(y, x + 1, chr)
            x = x + 1
        self.window.refresh()

class Battleline(Box):
    def __init__(self, window, width, height, x, y):
        super().__init__(window, width, height, x, y)
        self.window.border()
        self.setName("Battleline")

class Dialog(Box):
    def __init__(self, window, width, height, x, y):
        super().__init__(window, width, height, x, y)
        self.height = height
        self.width = width
        self.y = y
        self.x = x
        self.window.border()
        self.setName("Dialog")
        self.initInside(30)
        #self.window.scrollok(True)
        #self.window.idlok(True)
        sys.stdout = self

    def initInside(self, pad_height):
        self.inside = ScrollPad(self.width - 2, pad_height, self.x + 1, self.y + 1, self.height - 2)
        self.inside.refresh()

    def refresh(self):
        self.inside.refresh()
        self.window.refresh()
    
    def write(self, text):
        self.inside.write(text)
        
    def flush(self):
        curses.flushinp()

class Pad:
    def __init__(self, width, height, x, y):
        self.height = height
        self.width = width
        self.y = y
        self.x = x
        self.pad = curses.newpad(self.height, self.width)
        self.pad.scrollok(True)
        self.pad.idlok(True)

    def write(self, text):
        self.pad.addstr(text)
        self.pad.refresh(0, 0, self.y, self.x, 30, 20)

class ScrollPad(Pad):
    def __init__(self, width, height, x, y, col):
        super().__init__(width, height, x, y)
        self.col = col
        self.pad.move(self.height - 1, 0)

    def write(self, text):
        if all(ord(c) < 128 for c in text):
            self.pad.addstr(text)
        else:
            self.foreignwrite(text)
        self.refresh()

    #def foreignwrite(self, text=str):          #한글 포기;;
    #    for c in text:
    #        if ord(c) < 128:
    #            self.pad.addch(c)
    #        else:
    #            self.pad.addstr("  ")   #2글자 크기로 대체해서 일단 삽입
    #            if self.pad.getyx()[1] == 0:    #커서가 맨 앞이면 한글이었을 경우 직전 모서리에 끼임 -> 에러
    #                self.pad.addch(' ') #한 칸 더 확보
    #                #이제 한글이 들어갈 위치 확보됨.
    #            y, x = self.pad.getyx()
    #            self.pad.move(y, x - 1) #한글 삽입 위치로 이동
    #            self.pad.addch(c)   #이 경우 앞의 띄어쓰기 남음


    def refresh(self):
        self.pad.refresh(self.height - self.col, 0, self.y, self.x, self.y + self.col, self.x + self.width)

def main(stdscr):
    stdscr.clear()

    screen = Screen(stdscr)

    for _ in range(10):
        screen.dialog.write("testsfjeiiojvjeiovjeoijfojwicekwcjeewicjowejcikewoicjoiwejcfoejwvoiwejiockjfioekcjcocdjojeoijckojwojfodovwjcodwjovjwocvekidjowkfjcow\n")
    screen.dialog.write("another test")
    screen.dialog.inside.pad.getch()
    

if __name__ == '__main__':
    curses.wrapper(main)