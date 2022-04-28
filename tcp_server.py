import socket
import threading

HOST = "127.0.0.1"
PORT = 9999

def handle_client(client_socket):
    with client_socket as sock:
        req = sock.recv(1024)
        print(f'[*] Received: {req.decode("utf-8")}')
        sock.send(b'ACK')

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind((HOST, PORT))
server.listen(5)
print (f'Server Listening on {HOST}:{PORT}')
while True:
    client, address = server.accept()
    print (f"Accepted connection from {client} from {address}")
    client_handler = threading.Thread(target=handle_client, args=(client,))
    client_handler.start()




