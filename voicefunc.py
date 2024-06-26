#import time
import asyncio
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

defalt_voiceset = {
    'high': 740,
    'middle': 455,
    'low': 350,
    'sec': 0.11
}

class voice:
    def __init__(self, **voiceset):
        if voiceset == {}:
            voiceset = defalt_voiceset
        self.SEC = voiceset['sec']
        self.bip = generateBeep(voiceset["high"], self.SEC)
        self.bop = generateBeep(voiceset["middle"], self.SEC)
        self.bup = generateBeep(voiceset["low"], self.SEC)
        self.bip.set_volume(0.6)
        self.bop.set_volume(0.6)
        self.bup.set_volume(0.6)

    async def async_speakgen(self, line, accent, loop):
        for l, a in zip(line, accent):
            if l == ('!' or '?' or '.' or ',' or '-'):
                yield l
                await asyncio.sleep(self.SEC)
            elif a == ' ': #No verbal break
                yield l
            else:
                self.speakchar(a)
                yield l
                await asyncio.sleep(self.SEC)
    
    #line의 음절이 하나씩 들어 있는 generator이다. 글자 하나를 반환한다.
    #for 글자 in speakgen:
    #   뭔가 해라(글자)
    def speakgen(self, line:str, accent:str):
        if len(line) != len(accent):
            raise ValueError("linenum != accent!")
        else:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            gen = self.async_speakgen(line, accent, loop)
            while True:
                try:
                    yield loop.run_until_complete(gen.__anext__())
                except StopAsyncIteration:
                    break
            loop.close()
        yield '\n'

    def speakchar(self, accent:str):
            if accent == '-':
                self.bop.play()
            elif accent == '_':
                self.bup.play()
            elif accent == '^':
                self.bip.play()




#예시. 아래처럼 외부에서 voice 인스턴스를 생성해 speakgen을 반복해서 불러올 것.
def voiceFuncTest(voice:voice, line:str, accent:str):
    for chr in voice.speakgen(line, accent):
        print(chr, end='')
    
if __name__ == "__main__":
    samplevoice = voice()
    voiceFuncTest(samplevoice, "뭐라카노?", "_-^-.")
    voiceFuncTest(samplevoice, "니 내 누군지 아나?", "-.-.^^- _- ")