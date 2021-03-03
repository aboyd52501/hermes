from packet import Packet, EOTError
from threading import Thread
from sys import argv
from random import seed, randint
import socket

#def socket_send(self, )

def condition_socket(sock):
    sock.recv_original = sock.recv
    

class Server:

    def __init__(self, port):
        self.socket = socket.socket()
        self.socket.bind(('', port))
        
        self.listen()
    
    def listen(self):
        self.socket.listen()

        while True:
            conn, addr = self.socket.accept()
            new_client_thread = Thread(target=self.handle_client, args=(conn, addr))
            new_client_thread.start()
    
    @staticmethod
    def PRNG(data, byte_count):
        seed( Packet.decode_number(data) )
        return randint(0, 256**byte_count - 1)

    # abstract method
    def handle_client(self, conn, addr):
        raise NotImplementedError # don't forget 👁‍🗨

class CRCServer(Server):

    def handle_client(self, conn, addr):
        pretty_name = f"[{addr[0]}:{addr[1]}]"
        print(f"Connected {pretty_name}")
        while True:
            
            # this try-except statement lets us catch socket closures
            incoming_packet = Packet(0, None)
            try:
                incoming_packet = Packet.recv_over_socket(conn)
            except EOTError:
                break
            
            # just generate a pseudorandom code and respond with it
            code = CRCServer.PRNG(incoming_packet.full, 1)

            print(f"{pretty_name} : {incoming_packet}")
            print(f">>> {code}")

            outgoing_packet = Packet.from_string(str(code))
            outgoing_packet.send_over_socket(conn)
            
        print(f"Disconnected {pretty_name}")
        conn.close()

class OnceClient:

    def __init__(self, host, port):
        self.socket = socket.socket()
        self.socket.connect((host, port))

        self.handle_connection()
    
    def handle_connection(self):
        text_to_send = input(">>> ")
        outgoing_packet = Packet.from_text(text_to_send)
        outgoing_packet.send_over_socket(self.socket)

        incoming_packet = Packet.recv_over_socket(self.socket)
        print(bytearray(incoming_packet.content)[0])

class LoopClient(OnceClient):

    def handle_connection(self):
        while True:
            text_to_send = input(">>> ")

            if text_to_send == "/exit":
                self.socket.close()
                break

            outgoing_packet = Packet.from_string(text_to_send)
            outgoing_packet.send_over_socket(self.socket)

            incoming_packet = Packet.recv_over_socket(self.socket)
            print(incoming_packet)

import time
class TestOnceClient(OnceClient):

    def handle_connection(self):
        text_out = "a"*(2**20)
        
        outgoing_packet = Packet.from_string(text_out)
        print(outgoing_packet)

        curtime = time.time()
        outgoing_packet.send_over_socket(self.socket)

        response = Packet.recv_over_socket(self.socket)
        delta = time.time() - curtime
        print(response)
        
        print(f"{len(text_out)} bytes sent in {delta} seconds   ")

        self.socket.close()


if __name__ == "__main__":
    if argv[1] == "client":
        client = OnceClient(str(argv[2]), int(argv[3]))
    elif argv[1] == "loopclient":
        client = LoopClient(str(argv[2]), int(argv[3]))
    elif argv[1] == "testclient":
        client = TestOnceClient(str(argv[2]), int(argv[3]))
    elif argv[1] == "server":
        for i in range(40000, 40100):
            try:
                print(i)
                server = Server(i)
            except OSError:
                pass
    elif argv[1] == "crcserver":
        for i in range(40000, 40100):
            try:
                print(i)
                server = CRCServer(i)
            except OSError:
                pass
