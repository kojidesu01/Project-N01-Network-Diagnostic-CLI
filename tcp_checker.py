import socket

def check_tcp(ip, port):
    try:
        with socket.create_connection((ip, port), timeout=5) as connect:
            return True
    except ConnectionRefusedError:
        print("[REFUSED] Connection refused")
        return False
    except socket.timeout:
        print("[TIMEOUT] Connection timed out")
        return False