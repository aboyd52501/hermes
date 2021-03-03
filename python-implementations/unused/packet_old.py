from math import log, ceil

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

class VarInt:

    @staticmethod
    def encode(integer):
        b = bytearray()
        while integer >> 7 != 0:
            b.append( integer & 0b01111111 | 0b10000000 )
            integer >>= 7
        b.append( integer & 0b01111111 )
        return bytes(b)

    @staticmethod
    def decode( b ):
        integer = int()
        for k, v in enumerate( list( bytearray(b) ) ):
            integer |= ( int(v) & 0b01111111 ) << ( k * 7 )
            if int(v) & 0b10000000 == 0:
                break
        return integer, b[k+1:]

class Packet:

    type_byte = bytes([255])

    types = Map()
    types["Message"] = bytes([0])
    types["RSAKey"] = bytes([4])

    def __init__(self):
        self.data = []
    
    def add_data(self, *data):
        for byte_string in data:
            self.data.append(byte_string)
    
    def get_length_header(self, this_data):
        return VarInt.encode(len(this_data))

    def serialize(self):
        return b''.join(self.data)

    @staticmethod
    def encode_number(integer):
        byte_count = 1
        while 256**byte_count <= integer:
            byte_count += 1
        return integer.to_bytes(byte_count, 'big')

    @staticmethod
    def decode_number(data):
        return int.from_bytes(data, 'big')

class MessagePacket(Packet):
     
    type_byte = Packet.types["Message"]

    def __init__(self, text):
        super().__init__()

        self.text = text
        self.text_data = text.encode('utf-8')

        # LENGTH | TYPE | DATA
        self.add_data(
            self.get_length_header(self.text_data),
            self.type_byte,
            self.text_data
        )

    @staticmethod
    def decode(data_length, read_socket):
        data = bytes()
        data = 


class RSAKeyPacket(Packet):
    
    type_byte = Packet.types["RSAKey"]

    def __init__(self, n, e):
        super().__init__()

        self.n = n
        self.n_data = Packet.encode_number(n)
        self.n_data_length = VarInt.encode(len(self.n_data))

        self.e = e
        self.e_data = Packet.encode_number(e)
        self.e_data_length = VarInt.encode(len(self.n_data_length))

        self.body = self.n_data_length + self.n_data + self.e_data_length + self.e_data
        self.total_length = VarInt.encode(len(self.body))

        self.add_data(
            self.total_length,
            self.type_byte,
            self.body
        )

        