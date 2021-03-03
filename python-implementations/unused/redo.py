import socket
from threading import Thread, Event, Lock
from sys import argv

import packet

class MirrorServer:

    def __init__(self, port):
        self.socket = socket.socket()
        self.socket.bind(('', port))
        self.socket.listen()

        self.listen()
        #listen_thread = Thread(target=self.listen)
        #listen_thread.start()
    
    def listen(self):
        while True:
            client_socket, client_address = self.socket.accept()

            client_thread = Thread(target=self.handle_connection, args=(client_socket, client_address))
            client_thread.start()

    def handle_connection(self, connection, address):
        pretty_name = f"[{address[0]}:{address[1]}]"
        print(f"{pretty_name} connected")
        
        while True:
            data_in = connection.recv(4096)

            if data_in == b'\x00':
                break

            text_in = data_in.decode('utf-8')
            print(f"{pretty_name} :> {text_in}")

            connection.sendall(data_in)
            print(f"{text_in} :> {pretty_name}")
        
        print(f"{pretty_name} disconnected")

class SimpleCMDClient:
    
    def __init__(self, address, port):
        self.socket = socket.socket()
        self.socket.connect((address, port))

        self.loop()
    
    def loop(self):
        while True:
            text_out = input(">>> ")

            if text_out == "/exit":
                self.socket.send(b'\x00')
                self.socket.close()
                break

            data_out = text_out.encode('utf-8')
            self.socket.sendall(data_out)

            data_in = self.socket.recv(4096)
            text_in = data_in.decode('utf-8')
            print(f"{self.socket.getpeername()} :> {text_in}")


class ClientInterface:

    def __init__(self, target_address, target_port):
        self.socket = socket.socket()
        self.socket.connect((target_address, target_port))

        self.input_thread = Thread(self.listen)

if __name__ == "__main__":
    if argv[1] == "client":
        client = SimpleCMDClient('localhost', int(argv[2]))
    elif argv[1] == "server":
        for i in range(40000, 40100):
            try:
                print(i)
                server = MirrorServer(i)
            except OSError:
                pass
