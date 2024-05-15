from typing import Coroutine
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll
from textual.widgets import Header, Footer, Static
from textual.reactive import reactive
import RPGproject as pj

class Battlefield(Horizontal):
    def __init__(self, *args, UI: App | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        UI.battlefield = self
    
    def compose(self):
        yield Static("battlefield")

class Dialog(VerticalScroll, pj.Dialog):

    text = reactive([])
    ntext : str = reactive("")
    
    def __init__(self, *args, UI: App | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.text.append("This is dialog page.")
        self.text.append("This is the second line.")
        self.motherscreen = UI

    def compose(self):
        textgen = self.initwrite()
        for chr in textgen:
            yield Static(chr)
        
        for line in self.text:
            yield Static(line)

    def on_show(self):
        textgen = self.initwrite()
        yield Static(self.ntext)
        for chr in textgen:
            self.ntext += chr



class Screen(App):

    battlefield : Battlefield
    dialog : Dialog
    main : pj.Main

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode"),
                ("q", "exit", "Quit")]
    
    CSS = """
    Battlefield{
        border: white;
    }

    Dialog{
        border: white;
    }
    """
    
    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        yield Container(
            Horizontal(
                Battlefield(classes="box", UI=self),
                Dialog(classes="box", UI=self, id="dialog")
                )
            )

    def on_mount(self):
        self.main = pj.Main(self)

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark

    def action_exit(self):
        self.exit()

if __name__ == "__main__":
    app = Screen()
    app.run()
