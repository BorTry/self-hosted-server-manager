from tui.widgets.mini_widget import MiniWidget
from tui.widgets.mini_progress import MiniProgressBar

from textual.widgets import ProgressBar
from textual.containers import Middle, Center

from time import monotonic

class DockerContainer(MiniWidget):
    def __init__(self, border_title, **kwargs):
        super().__init__(border_title, **kwargs)
        self.cpu_bar = MiniProgressBar("CPU", id=f'{border_title}_CPU', classes="ResourceBar")
        self.ram_bar = MiniProgressBar("RAM", id=f'{border_title}_RAM', classes="ResourceBar")
        self.last_progress_update = monotonic()

    def compose(self):
        yield self.cpu_bar
        yield self.ram_bar

    def update_progress_bars(self, cpu_val:int, ram_val:int):
        self.cpu_bar.update_progress(cpu_val)
        self.ram_bar.update_progress(ram_val)