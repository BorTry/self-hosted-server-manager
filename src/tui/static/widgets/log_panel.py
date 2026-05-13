from textual.widgets import Log
from collections import deque

from .container import ScrollableContainer

class LogPanel(ScrollableContainer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __init__(self):
        self.log_el = Log()
        self.lines = deque(maxlen=100)
        super().__init__(self.log_el)

    def write(self, text:str):
        self.lines.append(text)

        self.log_el.clear()
        self.log_el.write_lines(list(self.lines))

    def clear(self):
        self.log_el.clear()