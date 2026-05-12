from textual.app import App
from textual.containers import Grid
from textual.widgets import Button, Footer

from src.tui.widgets.container import CustomContainer, CustomScrollContainer
from src.tui.widgets.mini_widget import MiniWidget
from src.tui.widgets.log_panel import LogPanel
from src.tui.widgets.docker_container import DockerContainer

from os import system, environ

from threading import Thread
from time import sleep

system('mode con: cols=200 lines=36')

environ["TEXTUAL_FPS"] = "10"

docker_containers = []
for i in range(15):
    docker_containers.append(DockerContainer(f'Docker_{i}'))

class actions(App):
    CSS_PATH = "tcss/app.css"

    BINDINGS = [
        ("q", "quit", "Quit"),
    ]

    def __init__(self):
        super().__init__()
        self.logs = LogPanel()
        self.curr_it = 0

    def compose(self):
        with Grid() as grid:
            grid.styles.grid_size_columns = 4
            grid.styles.grid_size_rows = 5

            Log_container = CustomContainer(
                "Logs",
                (2, 5),
                self.logs,
                layout="vertical",
            )

            Thread_container = CustomContainer(
                "Threads",
                (1, 4),
                MiniWidget("Docker", classes="Content_container Thread_container"),
                MiniWidget("Communication", classes="Content_container Thread_container"),
                MiniWidget("Socket", classes="Content_container Thread_container"),
                layout="vertical",
            )

            Docker_container =  CustomScrollContainer(
                "Docker Containers",
                (1, 5), 
                layout="vertical",
                *docker_containers
            )

            Buttons_container = CustomContainer(
                "Actions", 
                (1, 1), 
                Button("Stop", classes="ActionButtons"),
                Button("Restart", classes="ActionButtons")
            )

            yield Log_container
            yield Thread_container
            yield Docker_container
            yield Buttons_container

        yield Footer()

    def on_mount(self):
        self.set_interval(1, self.update)

    def update(self):
        for row in self.query(DockerContainer):
            row.update_progress_bars(self.curr_it, self.curr_it)
            self.curr_it += 0.05
            if self.curr_it >= 1:
                self.curr_it = 0
            row.update_status(self.curr_it > 0.5)

if __name__ == "__main__":
    app = actions()

    b = False

    def ooga():
        iter = 0
        while (True):
            if (b): return
            if (app.is_running):
                app.call_from_thread(app.logs.write, f'ooga {iter}')
                iter += 1
            sleep(0.1)

    t = Thread(target=ooga) 
    t.start()

    app.run()

    b = True

    t.join()
