class C:
    _text = ""

    @property
    def text(self):
        return self._text
    @text.setter
    def text(self, string):
        self._text = string

c = C()
c.text += 'abc'
c.text += 'ands'
print(c.text)