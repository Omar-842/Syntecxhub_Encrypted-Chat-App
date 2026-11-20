import socket
import threading

from simple_common import decrypt_message, encrypt_message

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("localhost", 5000))


def receive():
    for line in sock.makefile("rb"):
        try:
            print("\r" + decrypt_message(line.strip()))
        except Exception as e:
            print("\rbad message:", e)


threading.Thread(target=receive, daemon=True).start()

while True:
    msg = input()
    if msg == "/quit":
        break
    sock.sendall(encrypt_message(msg) + b"\n")
sock.close()
