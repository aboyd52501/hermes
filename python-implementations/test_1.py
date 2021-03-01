if __name__ == "__main__":
    
    import rsa
    import socket
    import threading
    import multiprocessing
    import sys
    from math import ceil, log

    multiprocessing.freeze_support()

    def send_msg(s, data):
        data_length = len(data)
        data_header = data_length.to_bytes(4, 'little')
        data_out = data_header + data

        s.sendall(data_out)
        #print(f"Sent {data}")

    def recv_msg(s):
        length_header = s.recv(4)
        if not length_header:
            return

        msg_length = int.from_bytes(length_header, 'little')
        received_byte_count = 0
        body = bytes(0)
        while received_byte_count < msg_length:
            new_segment = s.recv(min(4096, msg_length - received_byte_count))
            body += new_segment
            received_byte_count += len(new_segment)
        
        #print(f"Received {body}")
        return body
        
    def encode_large_int(INT):
        byte_count = ceil(log(INT,256))
        return INT.to_bytes(byte_count, 'big')

    def decode_large_int(data):
        return int.from_bytes(data, 'big')

    def send_pubkey(sock, key):
        n_data = encode_large_int(key.n)
        e_data = encode_large_int(key.e)
        send_msg(sock, n_data)
        send_msg(sock, e_data)

    def recv_pubkey(sock):
        n_data = recv_msg(sock)
        e_data = recv_msg(sock)
        n = decode_large_int(n_data)
        e = decode_large_int(e_data)
        return rsa.PublicKey(n, e)

    class Server:
        
        def __init__(self, port):
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.pubkey, self.privkey = rsa.newkeys(1024, poolsize=4)
            self.connections=[]

            self.sock.bind(('', port))
            self.sock.listen()

        def encrypt(self, data, pubkey):
            return rsa.encrypt(data, pubkey)
        
        def decrypt(self, data):
            return rsa.decrypt(data, self.privkey)
        
        def encrypt_and_broadcast(self, data):
            for id, connection_object in enumerate(self.connections):
                thisclient_conn, thisclient_addr, thisclient_pubkey = connection_object
                data_e = self.encrypt(data, thisclient_pubkey)
                send_msg(thisclient_conn, data_e)

        def handler(self, conn, addr, client_pubkey):
            # send server's key
            send_pubkey(conn, self.pubkey)
            # start chat session
            print(f"Connected {addr}")
            while True:
                # get client message
                data_encrypted = recv_msg(conn)
                if not data_encrypted:
                    print(f"Disconnected {addr}")
                    break

                data = self.decrypt(data_encrypted)
                text = data.decode()

                text = ''.join(c for c in text if c.isprintable())

                name = f"[{addr[0]}:{addr[1]}]"
                print(f"{name} => {text}")

                text_out = f"{name} : {text}"
                data_out = text_out.encode()

                #send to all clients
                self.encrypt_and_broadcast(data_out)
                print(f"{len(self.connections)} clients <= {text_out}")
        
        def run(self):
            while True:
                conn, addr = self.sock.accept()

                # receive client public key
                client_pubkey = recv_pubkey(conn)
                self.connections.append((conn, addr, client_pubkey))

                conn_thread = threading.Thread(target=self.handler, args=(conn, addr, client_pubkey))
                conn_thread.daemon = True
                conn_thread.start()

    class Client:

        def encrypt(self, data):
            return rsa.encrypt(data, self.server_pubkey)
        
        def decrypt(self, data):
            return rsa.decrypt(data, self.privkey)

        def send_message(self):
            while True:
                text_out = input()
                chunks = []
                while len(text_out):
                    chunks.append(text_out[:63])
                    text_out = text_out[63:]
                
                for text in chunks:
                    send_msg(self.sock, self.encrypt(text.encode()))

        def __init__(self, addr, port):
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.pubkey, self.privkey = rsa.newkeys(1024, poolsize=4)
            self.sock.connect((addr, port))

            # exchange keys
            send_pubkey(self.sock, self.pubkey)
            self.server_pubkey = recv_pubkey(self.sock)

            # input thread
            input_thread = threading.Thread(target=self.send_message)
            input_thread.daemon = True
            input_thread.start()

            # receive messages from the server
            try:
                while True:
                    data_encrypted = recv_msg(self.sock)
                    if not data_encrypted: break
                    data = self.decrypt(data_encrypted)
                    text = data.decode()
                    print(text)
            except KeyboardInterrupt:
                self.sock.close()
                exit()

    if len(sys.argv) < 2:
        print("Please specify 'client targetIP port' or 'server port!")
        exit()
    else:
        if sys.argv[1] == "client":
            client = Client(sys.argv[2], int(sys.argv[3]))
        elif sys.argv[1] == "server":
            server = Server(int(sys.argv[2]))
            server.run()
