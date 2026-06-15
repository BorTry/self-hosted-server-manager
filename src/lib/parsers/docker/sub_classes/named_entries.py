from .named_entries_base import named_entry_base

class service(named_entry_base):
    __slots__ = ("container_name", "image", "ports", "build", "volumes", "working_dir", "user", "environment", "networks", "cpus", "mem_limit", "command")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class network(named_entry_base):
    __slots__ = ("driver", "external", "internal", "custom_name")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class volume(named_entry_base):
    __slots__ = ("external", "custom_name")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class project_name:
    __slots__ = ("name", )

    def __init__(self, name=None):
        self.name = name

    def __repr__(self):
        return f"{self.name}" + "\n"