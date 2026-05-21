from textual.widgets import Log

from .container import ScrollableContainer
from src.lib import get_logger

MAX_LENGTH = 300

class LogPanel(ScrollableContainer):
    def __init__(self, **kwargs):
        self.log_el = Log()
        self.logger = get_logger("Logpanel", self.write)
        self.lines = self.logger.get_history()
        self.length = 0

        super().__init__(self.log_el, **kwargs)

    def on_mount(self):
        for line in self.lines:
            self.write(line)

    def write(self, *text:list[str]):
        if not self.is_running: return

        if self.length >= MAX_LENGTH:
            self.lines = self.logger.get_history()

            for line in self.lines:
                self.write(line)
            self.length = 0

        string = ""

        for entry in text:
            string += f'{entry} '

        self.log_el.write_line(f'{string}\n')
        self.length += 1

    def clear(self):
        self.log_el.clear()