from src.tui.widgets.mini_progress import MiniProgressBar
from src.tui.widgets.mini_widget import MiniWidget

from textual.containers import Horizontal, Vertical
from textual.widgets import Button

class DockerContainer(MiniWidget):
    def __init__(self, border_title, **kwargs):
        super().__init__(border_title, classes="Content_container", **kwargs)
        self.cpu_bar = MiniProgressBar("CPU", id=f'{border_title}_CPU', classes="ResourceBar")
        self.ram_bar = MiniProgressBar("RAM", id=f'{border_title}_RAM', classes="ResourceBar")
        self.status = MiniWidget("", "Offline", classes="Status_text")

    def compose(self):
        with Horizontal() as hor:
            hor.styles.height = "auto"

            yield MiniWidget("", "Status : ", classes="Status_text")
            yield self.status

        with Vertical() as ver:
            ver.styles.height = "auto"
            
            yield self.cpu_bar
            yield self.ram_bar

        with Horizontal() as hor:
            hor.styles.height = "auto"
            hor.styles.align_horizontal = "center"

            yield Button("Start", classes="Docker_button")
            yield Button("Stop", classes="Docker_button")
            yield Button("Restart", classes="Docker_button")

    def update_progress_bars(self, cpu_val:int, ram_val:int):
        self.cpu_bar.update_progress(cpu_val)
        self.ram_bar.update_progress(ram_val)

    def update_status(self, status:bool):
        self.status.styles.color = "green" if status else "red"
        self.status.inner_text = "Running" if status else "Offline"