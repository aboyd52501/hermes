### Packet Header
Every packet has a five-byte header, with the first four bytes specifying the length of the data segment and the last byte specifying the type of data it contains.
The first four bytes are a little-endian unsigned 32 bit integer.\
`| Length 1 | Length 2 | Length 3 | Length 4 | Type 1 | Data Segment... |` 

### Data Segment Types:
| Data Type     | Type ID | Type Bits |
| ------------- | ------- | --------- |
| Message       |    0x00 | 00000000  |
| Roster        |    0x01 | 00000001  |
| RSA Key       |    0x04 | 00000100  |
| AES Key       |    0x05 | 00000101  |
| RSA Encrypted |    0x08 | 00001000  |
| AES Encrypted |    0x09 | 00001001  |
| Redirect      |    0x0C | 00001100  |
| Chain         |    0x0D | 00001101  |
| Audio Begin   |    0x10 | 00010000  |
| Audio Data    |    0x11 | 00010001  |
| Audio End     |    0x12 | 00010010  |

#### `0x00` Message
  The message datatype is a single string of UTF-8 encoded characters.\
  `| UTF-8 Byte Array |`
  
#### `0x01` Roster
  Currently Undefined
  
#### `0x04` RSA Key
  The RSA Key data type contains a modulus and exponent for building a public key to encrypt RSA packets. It has two little-endian uint16 length values and two variable size byte arrays.\
  `| Length 1 | Length 2 | Modulus Byte Array | Length 1 | Length 2 | Exponent Byte Array |`
  
#### `0x05` AES Key
  The AES Key data type contains a key and iv for encrypting and decrypting AES packets. It has two little-endian uint16 length values and two variable size byte arrays.\
  `| Length 1 | Length 2 | Key Byte Array | Length 1 | Length 2 | IV Byte Array |`
  
#### `0x08` RSA Encrypted
  The RSA Encrypted data type is a meta datatype with a single byte array. Another fully compounded packet is encrypted with an RSA public key and placed inside of this packet's data payload.\
  `| Encrypted Mesa Packet |`
  
  
#### `0x09` AES Encrypted
  The AES Encrypted data type is a meta datatype with a single byte array. Another fully compounded packet is encrypted with AES and placed inside of this packet's data payload.\
  `| Encrypted Mesa Packet |`
  
#### `0x0C` Redirect
  Currently Undefined
  
#### `0x0D` Chain
  Currently Undefined
  
#### `0x10` Audio Begin
  Currently Undefined
  
#### `0x11` Audio Data
  Currently Undefined
  
#### `0x12` Audio End
  Currently Undefined
  
  
  
