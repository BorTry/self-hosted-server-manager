from ..docker import *
from src.lib import thread_wrapper, Server_codes

from src.db.mappings import launch_opts_view
from src.db.db import SessionLocal

from sqlalchemy import select

def docker_handler_func(thread:thread_wrapper):
    requests = thread.data_handler.get_copy("requests")
    responses = thread.data_handler.get_copy("responses")

    with thread.data_handler as data:
        data["requests"] = []

    if (not len(requests)): return
    
    for data_packet in requests:
        match (data_packet.code):
            case Server_codes.START_SERVER:
                start_server(data_packet.data["name"])
                _get_launch_opts(thread, data_packet.data["name"])

            case Server_codes.STOP_SERVER:
                stop_server(data_packet.data["name"])

            case Server_codes.RESTART_SERVER:
                restart_server(data_packet.data["name"])

    with thread.data_handler as data:
        data["responses"] = responses

def docker_handler_init(thread:thread_wrapper):
    pass

def _get_launch_opts(thread:thread_wrapper, container_name:str):
    # retrieve the launch options from the database
    # check if there are any launch options

    with SessionLocal() as session:
        rows = session.execute(select(launch_opts_view).where(launch_opts_view.s_name == container_name)).mappings().all()
        existing_opts = [dict(row) for row in rows]

        thread.print(existing_opts)


    pass