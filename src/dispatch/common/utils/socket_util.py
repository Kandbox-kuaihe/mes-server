import socket


def get_local_ip():
    return socket.gethostbyname(socket.gethostname())
