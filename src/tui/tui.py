from textual import on
from textual.app import App
from textual.containers import Grid
from textual.widgets import Button, Footer

from src.tui.static.widgets import CustomContainer, CustomScrollContainer, MiniWidget, LogPanel, DockerContainer
from src.lib import thread_data_handler, Server_codes

from os import environ

environ["TEXTUAL_FPS"] = "10"

class TextualApp(App):
    CSS_PATH = "static/tcss/app.css"

    BINDINGS = [
        ("q", "quit", "Quit"),
    ]

    def __init__(self, data_handler:thread_data_handler=None):
        self.logs = LogPanel()

        super().__init__()

        self.data_handler = data_handler

        self.docker_containers = []
        
        self.Log_container = None
        self.Thread_container = None
        self.Docker_container = None
        self.Buttons_container = None
        self.Front_end_container = None

        self._parse_container_names()

    def compose(self):
        with Grid() as grid:
            grid.styles.grid_size_columns = 4
            grid.styles.grid_size_rows = 5

            self.Log_container = CustomContainer(
                "Logs",
                (2, 5),
                self.logs,
                layout="vertical",
            )

            self.Thread_container = CustomContainer(
                "Threads",
                (1, 2),
                MiniWidget("Docker", classes="Content_container Thread_container"),
                MiniWidget("Socket", classes="Content_container Thread_container"),
                layout="vertical",
            )
            

            self.Docker_container =  CustomScrollContainer(
                "Docker Containers",
                (1, 5), 
                layout="vertical",
                *self.docker_containers
            )

            self.Front_end_container = CustomContainer(
                "Frontend", 
                (1, 2),
                DockerContainer("Frontend", add_buttons=False, id="Frontend"),
            )
            
            self.Buttons_container = CustomContainer(
                "Actions", 
                (1, 1), 
                Button("Stop", classes="ActionButtons"),
                Button("Restart", classes="ActionButtons")
            )

            yield self.Log_container
            yield self.Thread_container
            yield self.Docker_container
            yield self.Front_end_container
            yield self.Buttons_container

        yield Footer()
    
    @on(Button.Pressed)
    def handle_press(self, event:Button.Pressed):
        name, action_name = event.button.id.split("-")
        
        code = Server_codes.START_SERVER 

        if action_name == "stop":
            code = Server_codes.STOP_SERVER

        if action_name == "restart":
            code = Server_codes.RESTART_SERVER 

        data_packet = {
            "code": code,
            "data": {"name": name.replace("_", " ")}
        }

        with self.data_handler as data:
            data["requests"].append(data_packet)

    def on_mount(self):
        self.set_interval(0.5, self.parse_container_info)
       # self.set_interval(0.5, lambda _: self.logs.logger.log("hello"))

    def parse_container_info(self):
        if not self.data_handler: return

        # update all containers to be in their default state
        for rows in self.Docker_container.children:
            rows.update_progress_bars(0, 0)
            rows.update_status(False)

        containers = None
        # Get all the container information in the data
        with self.data_handler as data:
            containers = data["data"][Server_codes.RUNNING_SERVERS]
            if (not containers or not len(containers)): return

            containers = data["data"][Server_codes.RUNNING_SERVERS].copy()

        for container in containers:
            textual_container = self.Docker_container.query_one(f'#{parse_name(container["name"])}')
            textual_container.update_progress_bars(container["cpu"]/100, container["ram"]/100)
            textual_container.update_status(True)

    def _parse_container_names(self):
        # Get the name of all available server
        if not self.data_handler: return

        containers = None
        # Get all the container information in the data
        with self.data_handler as data:
            containers = data["data"][Server_codes.ALL_SERVERS]

            if (not containers or not len(containers)): return
            containers = data["data"][Server_codes.ALL_SERVERS]["servers"].copy()

        for container in containers:
            self.docker_containers.append(DockerContainer(parse_name(container), id=parse_name(container)))

def parse_name(name:str):
    return name.replace(" ", "_")