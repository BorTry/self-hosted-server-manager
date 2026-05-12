from textual.widget import Widget
from textual.containers import ScrollableContainer

class CustomContainer(Widget):   
    def __init__(self, border_title:str, span:tuple[int, int], *children:Widget, layout="horizontal", **kwargs):
        super().__init__(*children, **kwargs)

        self.border_title = border_title
        if span:
            self.styles.row_span = span[1]
            self.styles.column_span = span[0]

        if layout:
            self.layout_type = layout

    def on_mount(self) -> None:
        if self.layout_type:
            self.styles.layout = self.layout_type

class CustomScrollContainer(ScrollableContainer):   
    def __init__(self, border_title:str, span:tuple[int, int], *children:Widget, layout="horizontal", **kwargs):
        super().__init__(*children, **kwargs)

        self.border_title = border_title
        self.styles.row_span = span[1]
        self.styles.column_span = span[0]

        self.layout_type = layout

    def on_mount(self) -> None:
        self.styles.layout = self.layout_type