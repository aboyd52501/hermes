from threading import Thread, Event
from sys import argv
import socket

class Map(dict):
        def __setitem__(self, key, value):
            if key in self:
                del self[key]
            if value in self:
                del self[value]
            dict.__setitem__(self, key, value)
            dict.__setitem__(self, value, key)
        
        def __delitem__(self, key):
            dict.__delitem__(self, self[key])
            dict.__delitem__(self, key)
        
        def __len__(self):
            return super().__len__(self) // 2
            

DATATYPES = Map()
DATATYPES["Plaintext"] = 0
DATATYPES["Ciphertext"] = 1
DATATYPES["RSA Key Request"] = 2
DATATYPES["RSA Key Response"] = 3

LENGTH_HEADER_SIZE = 4
DATATYPE_HEADER_SIZE = 1

# msg is a 2-tuple of (datatype, data)
def send_message(socket, msg):
    datatype = msg[0]
    data = msg[1]

    length_header = len(data).to_bytes(LENGTH_HEADER_SIZE, 'little')
    datatype_header = datatype.to_bytes(DATATYPE_HEADER_SIZE, 'little') 

    data_out = length_header + datatype_header + data
    socket.sendall(data_out)

def recv_message(socket):
    length_header = socket.recv(LENGTH_HEADER_SIZE)
    datatype_header = socket.recv(DATATYPE_HEADER_SIZE)

    datatype = int.from_bytes(datatype_header, 'little')
    data_length = int.from_bytes(length_header, 'little')

    bytes_received = 0
    data_in = bytes()
    while bytes_received < data_length:
        bytes_to_read = min(4096, data_length-bytes_received)
        bytes_received += bytes_to_read
        data_in = data_in + socket.recv(bytes_to_read)

    return (datatype, data_in)

class Server:

    def __init__(self):
        self.connections = []
        self.running = True

    def attach(self, address, port):
        self.socket = socket.socket()
        self.socket.bind((address, port))
        self.socket.listen()

        # listen for incoming connections
        while self.running:
            # this line is blocking
            connection_socket, connection_address = self.socket.accept()
            
            # once a new connection comes in, delegate it to a handler thread
            new_connection_thread = Thread(
                target=self.handle_incoming_connection,
                args=(connection_socket, connection_address))
            new_connection_thread.daemon = False
            new_connection_thread.start()


    def handle_incoming_connection(self, connection, address):
        try:
            print(f"Connected {address}")
            while self.running:
                data_in_type, data_in = recv_message(connection)
                print(f"\nAddress: {address}\nType: {DATATYPES[data_in_type]}\nContent: {data_in.decode('utf-8')}")
                data_out = data_in[::-1]
                data_out_type = data_in_type
                send_message(connection, (data_out_type, data_out))
        except Exception as e:
            print(e)
        finally:
            print(f"Disconnected {address}")


    def close(self):
        self.running = False
        self.socket.close()

class Client:
    
    def __init__(self):
        self.inbox = []
        self.outbox = []
        self.can_send = Event()
        self.can_recv = Event()
        self.attached = False
        self.running = True

    def attach(self, target_address, target_port):
        self.socket = socket.socket()
        self.socket.connect((target_address, target_port))
        self.attached = True

        self.input_thread = Thread(target=self.listen_to_server, args=())
        self.input_thread.daemon = True
        self.input_thread.start()

        self.output_thread = Thread(target=self.listen_to_input)
        self.output_thread.daemon = True
        self.output_thread.start()


    def listen_to_server(self):
        try:
            while True:
                new_message = recv_message(self.socket)
                self.inbox.append(new_message)

                self.can_recv.set()
        except Exception as e:
            print(f"Exception {e} occurred.\nShutting down socket.")
            self.close()
    
    def listen_to_input(self):
        try:
            while True:
                self.can_send.wait()
                for msg in self.outbox:
                    send_message(self.socket, msg)
                self.outbox = []
                self.can_send.clear()        
        except Exception as e:
            print(f"Exception {e} occurred.\nShutting down socket.")
            self.close()

    # non-blocking
    def queue_message(self, msg):
        self.outbox.append(msg)
        self.can_send.set()
    
    def get_output(self):
        self.can_recv.wait()
        out = self.inbox
        # clear the inbox and reset the can_receive Event
        self.inbox = []
        self.can_recv.clear()
        return out
 
    def close(self):
        self.running = False
        self.can_send.set()
        self.can_recv.set()
        self.input_thread.join()
        print("Input thread joined")
        self.output_thread.join()
        print("Output thread joined")
        self.socket.close()

class ConsoleIO:
    def __init__(self, address, port):
        self.client = Client()
        self.client.attach(address, port)
        try:
            while self.client.running:
                text_out = input(">>> ")
                data_out = text_out.encode('utf-8')

                self.client.queue_message((DATATYPES["Plaintext"], data_out))

                msg_in = self.client.get_output()
                for msg in msg_in:
                    print(msg) 
        except KeyboardInterrupt:
            print("\nExiting, goodbye!")
        except Exception as e:
            print(e)
        finally:
            self.client.close()


if __name__ == "__main__":
    if argv[1] == "client":
        c = ConsoleIO(argv[2], int(argv[3]))
    elif argv[1] == "server":
        s = Server()
        s.attach('', int(argv[2]))