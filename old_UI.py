import pygame

pygame.font.init()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

class Box(pygame.Surface):
    Boxfont = pygame.font.SysFont("malgungothic", 15)
    
    def __init__(self, x, y, width, height, display):
        super().__init__((width, height))
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.motherscreen = display
        self.rect = pygame.Rect(x, y, width, height)

        self.fill(WHITE)
        self.drawBorder()
        print("called")

    def drawBorder(self):
        try:
            pygame.draw.rect(self, BLACK, (0,0,self.width, self.height), 5, 2)
        except:
            print("couldn't draw border!")

    def drawBoxName(self, name: str, x=10, y=6):
        self.blit(
            pygame.font.SysFont("malgungothic", 15, bold=True, italic=True).render(name, True, BLACK),
            (x, y))

class Battlefield(Box):
    def __init__(self, x, y, width, height, display):
        super().__init__(x, y, width, height, display)
        self.drawBoxName("Battlefield")

class Dialog(Box):
    terminal = [pygame.Surface]
    lastline = ''
    
    def __init__(self, x, y, width, height, display):
        super().__init__(x, y, width, height, display)
        self.drawBoxName("Dialog")
        self.setDialog("malgungothic", 10, 4)
        self.pad = pygame.Surface((self.width - 10, self.height - 10))

    def setDialog(self, fontname, fontsize, offset):
        self.fontsize = fontsize
        self.offset = offset + fontsize
        self.dialogfont = pygame.font.SysFont(fontname, fontsize)

    def write(self,text):
        if self.lastline == '':
            self.pad.scroll(0, self.offset)
        else:
            self.terminal.pop(-1)
        
        parsedtext, textend = parse((self.width - 10) // self.fontsize, text)
        
        for line in parsedtext:
            self.terminal.append(self.dialogfont.render(self.lastline + line, 0, BLACK))
            self.pad.scroll(0, self.offset)
            self.pad.blit(self.terminal[-1], (0, self.height - self.offset))

        if textend == True:
            self.lastline == ''

        self.blit(self.pad, (self.width - 5, self.height - 5))
        self.motherscreen.blit(self, self.rect)
        print("called!")

def parse(width, text: str):
    if text[-1] == '\n':
        textend = True
        text.pop(-1)
    else:
        textend = False
    texts = [text[i:i+width] for i in range(0, len(text), width)]
    return texts, textend



