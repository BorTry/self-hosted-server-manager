from flask import request

def get_user_ip():
    return request.remote_addr