import logging
import socket
import threading

from simple_common import decrypt_message, encrypt_message

logging.basicConfig(filename="simple_chat.log", level=logging.INFO,
                    format="%(asctime)s %(message)s")

clients = []
lock = threading.Lock()


def broadcast(text, sender_conn):
    data = encrypt_message(text) + b"\n"
    with lock:
        for conn, _ in clients:
            if conn is not sender_conn:
                try:
                    conn.sendall(data)
                except OSError:
                    pass


def handle(conn, addr):
    print(f"Connected by {addr}")
    f = conn.makefile("rb")
    try:
        for line in f:
            data = line.strip()
            if not data:
                continue
            print(f"Encrypted data received by server is: {data.decode()}")
            text = decrypt_message(data)
            print(f"AFTER Decryption message: {text}")
            logging.info("%s:%s %s", addr[0], addr[1], text)
            broadcast(f"{addr[1]}: {text}", conn)
    except Exception as e:
        print(f"Dropping {addr}: {e}")
    finally:
        with lock:
            clients.remove((conn, addr))
        conn.close()
        print(f"{addr} disconnected")


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(("localhost", 5000))
server_socket.listen(5)
print("Server listening on port 5000...")

while True:
    conn, addr = server_socket.accept()
    with lock:
        clients.append((conn, addr))
    threading.Thread(target=handle, args=(conn, addr), daemon=True).start()
