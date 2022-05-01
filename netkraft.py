#!/usr/bin/env python3

import shlex
import sys
import subprocess
import argparse
import socket
import threading
import os

def execute(cmd):

    cmd = cmd.strip()
    if not cmd: # incase of a random enter or Ctrl+D
        return 
    op = subprocess.check_output(shlex.split(cmd), stderr=subprocess.STDOUT)
    return (op.decode())


def handle_client(client_socket, server_socket, args):

    ####### Upload Logic
    if args.upload:
        file_buffer = b""
        while True:
            data = client_socket.recv(4096)
            if data:
                file_buffer += data
                print("Bytes Uploaded: " + str(len(file_buffer)))
            else:
                message = f"Saved file {args.upload}"
                client_socket.send(message.encode())
                break
        with open(args.upload, "wb") as f:
            f.write(file_buffer)
    
    ####### Mini Shell / Command Shell logic
    elif args.command:
        cmd_buffer = b""
        while True:
            try:
                client_socket.send(b"\nNETKRAFT #> ")
                while "\n" not in cmd_buffer.decode():
                    cmd_buffer += client_socket.recv(64)
                response = execute(cmd_buffer.decode())
                if response:
                    client_socket.send(response.encode())
                cmd_buffer = b""
            except UnicodeDecodeError: # Weird! Client interrupts could not be parsed as interrupts by server. Byte Codes?
                print(f"server killed due to client keyboard interrupt")
                server_socket.close()
                client_socket.close()
                os.system('kill -9 $PPID') # somehow sys.exit() doesn't seem to do the trick

            except FileNotFoundError as fnf: # Wrong command or filename
                print(f"Seems like a wrong command: {fnf}")
                client_socket.send(b"Error: Wrong command or filename\n")
                cmd_buffer = b""

class NetKraft:

    def __init__(self, args, buffer=""):
        self.args = args
        self.buffer = buffer
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

    def run(self):
        if self.args.listen:
            self.socket.bind(('0.0.0.0', self.args.port))
            self.socket.listen(5)
            print (f'[*] Listening at port {self.args.port} on all local IP addresses...')
            print (f'[*] Waiting for connection')

            while True:
                try:
                    client, _ = self.socket.accept()
                    print (f'[*] >>>> Accepted Connection from {client}')
                    client_handler = threading.Thread(target=handle_client, args=(client, self.socket, self.args))
                    client_handler.start()       
                except KeyboardInterrupt:
                    sys.exit()
        else:
            self.send()
            
    def send(self):
        """Send data to the target host."""
        self.socket.connect((self.args.target, self.args.port))
        if self.buffer:
            self.socket.send(self.buffer)

            
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--command", action="store_true", help="initialize command shell")
    parser.add_argument("-l", "--listen", action="store_true", help="listen")
    parser.add_argument("-p", "--port", type=int, default=5555, help="specified port")
    parser.add_argument("-t", "--target", default="192.168.1.203", help="specified IP")
    parser.add_argument("-u", "--upload", help="upload file")
    args = parser.parse_args()
    
    if args.listen:
        buffer = ""
    else:
        buffer = sys.stdin.read()

    nc = NetKraft(args, buffer.encode("utf-8"))
    nc.run()