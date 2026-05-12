from textual.widget import Widget

class MiniWidget(Widget):  
    def __init__(self, border_title:str, **kwargs):
        super().__init__(**kwargs)

        self.border_title = border_title

    def render(self):
        return ""