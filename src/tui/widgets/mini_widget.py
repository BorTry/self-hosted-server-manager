from textual.widget import Widget
from textual.reactive import reactive

class MiniWidget(Widget):  
    inner_text = reactive("")
    
    def __init__(self, border_title:str, text:str="", **kwargs):
        super().__init__(**kwargs)

        self.border_title = border_title
        self.inner_text = text

    def render(self):
        return self.inner_text