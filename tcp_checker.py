import socket

def check_tcp(ip, port):
    try:
        with socket.create_connection((ip, port), timeout=5) as connect:
            return True
    except ConnectionRefusedError:
        return False