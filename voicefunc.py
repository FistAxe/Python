import time
import numpy as np
import pygame

SEC = 0.11

pygame.mixer.init(frequency=44100, size=32, channels=2)
print(pygame.mixer.get_init())

def generateBeep(frequency, duration = 0.11):
    wave = np.sin(2 * np.pi * frequency * np.arange(44100 * duration) / 44100).astype(np.float32)
    wave = np.column_stack((wave, wave))
    beep = pygame.sndarray.make_sound(wave)
    return beep

bip = generateBeep(740, SEC)
bop = generateBeep(455, SEC)
bup = generateBeep(350, SEC)

class voice:
    def __init__(self, high=740, middle=455, low=350, sec=0.11):
        self.SEC = sec
        self.bip = generateBeep(high, self.SEC)
        self.bop = generateBeep(middle, self.SEC)
        self.bup = generateBeep(low, self.SEC)
        self.bip.set_volume(0.6)
        self.bop.set_volume(0.6)
        self.bup.set_volume(0.6)
    
    def speakgen(self, line:str, accent:str):
        if len(line) != len(accent):
            raise ValueError("linenum != accent!")
        for l, a in zip(line, accent):
            if l == ('!' or '?' or '.' or ',' or '-'):
                yield l
                time.sleep(self.SEC)
            elif a == ' ': #No verbal break
                yield l
            else:
                self.speakchar(a)
                yield l
                time.sleep(self.SEC)
        yield '\n'

    def speakchar(self, accent:str):
            if accent == '-':
                self.bop.play()
            elif accent == '_':
                self.bup.play()
            elif accent == '^':
                self.bip.play()

def speak(voice:voice, text:str, accent:str):
    for chr in voice.speakgen(text, accent):
        print(chr, end='')

def voiceFuncTest():
    samplevoice = voice()
    speak(samplevoice, "뭐라카노?", "_-^-.")
    speak(samplevoice, "니 내 누군지 아나?", "-.-.^^- _- ")
    
if __name__ == "__main__":
    voiceFuncTest()