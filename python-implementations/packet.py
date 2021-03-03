class EOTError(Exception):
    pass

class VarInt:

    @staticmethod
    def encode(integer):
        b = bytearray()
        while integer >> 7 != 0:
            b.append( (integer & 0b01111111) | 0b10000000 )
            integer >>= 7
        b.append( integer & 0b01111111 )
        return bytes(b)

    @staticmethod
    def decode( b ):
        integer = int()
        for k, v in enumerate( list( bytearray(b) ) ):
            integer |= ( int(v) & 0b01111111 ) << ( k * 7 )
            if (int(v) & 0b10000000) == 0:
                break
        return integer
    
    @staticmethod
    def recv_over_socket(conn):
        bytes_received = bytes()

        while True:
            in_byte = conn.recv(1)
            if not in_byte:
                raise EOTError
            bytes_received += in_byte

            if (bytearray(in_byte)[0] & 0b10000000) == 0:
                break
        
        varint_bytes = bytes_received
        return VarInt.decode(varint_bytes)

class Packet:

    def __init__(self, datatype, data):
        self.data = data
        self.datatype = datatype
        self.datatype_header = Packet.encode_number(datatype)
        if data:
            self.length_header = VarInt.encode(len(data))
            self.full = self.length_header + self.datatype_header + self.data
        else:
            self.length_header = VarInt.encode(0)
            self.full = self.length_header + self.datatype_header
    
    def send_over_socket(self, conn):
        conn.sendall(self.full)
    
    def decode(self):

        if self.datatype == 0:
            return self.content.decode('utf-8')
        elif self.datatype == 4:
            return # TODO: find an encryption library lol

    def __str__(self):
        return f"Packet( {self.datatype}, {self.data[0:128]} )"
    
    def __repr__(self):
        return f"Packet( {self.full} )"

    @staticmethod
    def recv_over_socket(conn):
        data_length = VarInt.recv_over_socket(conn)
        data_type = Packet.decode_number(conn.recv(1))

        bytes_received = bytes()
        while len(bytes_received) < data_length:
            read_length = min(4096, data_length)
            bytes_received += conn.recv(read_length)
        
        return Packet(data_type, bytes_received)

    @staticmethod
    def encode_number(integer):
        byte_count = 1
        while 256**byte_count <= integer:
            byte_count += 1
        return integer.to_bytes(byte_count, 'little')

    @staticmethod
    def decode_number(data):
        return int.from_bytes(data, 'little')
    
    @staticmethod
    def from_string(string):
        datatype = 0 # Messages are 0
        data = string.encode('utf-8')

        return Packet(datatype, data)
    
    @staticmethod
    def from_rsa_key(n, e):
        datatype = 4

        n_data = Packet.encode_number(n)
        e_data = Packet.encode_number(e)

        n_length_data = VarInt.encode(len(n_data))
        e_length_data = VarInt.encode(len(e_data))

        body = n_data_length + n_data + e_length_data + e_data

        return Packet(datatype, body)

