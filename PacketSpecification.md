### Packet Types:
<table>
	<tr><th>Name</th>          <th>ID</th>   <th>Bitmask</th></tr>
	<tr><td>Message</td>       <td>0x00</td> <td>00000000</td></tr>
	<tr><td>Roster</td>        <td>0x01</td> <td>00000001</td></tr>
	<tr><td>RSA Key</td>       <td>0x04</td> <td>00000100</td></tr>
	<tr><td>AES Key</td>       <td>0x05</td> <td>00000101</td></tr>
	<tr><td>RSA Encrypted</td> <td>0x08</td> <td>00001000</td></tr>
	<tr><td>AES Encrypted</td> <td>0x09</td> <td>00001001</td></tr>
	<tr><td>Redirect</td>      <td>0x0C</td> <td>00001100</td></tr>
	<tr><td>Chain</td>         <td>0x0D</td> <td>00001101</td></tr>
	<tr><td>Audio Begin</td>   <td>0x10</td> <td>00010000</td></tr>
	<tr><td>Audio Data</td>    <td>0x11</td> <td>00010001</td></tr>
	<tr><td>Audio End</td>     <td>0x12</td> <td>00010010</td></tr>
</table>

### Data Types
<table>
	<tr><th>Name</th>              <th>Bytes</th>               <th>Encodes</th></tr>
	<tr><td>Boolean</td>           <td>1</td>                   <td>True <code>0x01</code> or False <code>0x00</code></td></tr>
	<tr><td>Byte</td>              <td>1</td>                   <td>Integer between <code>-128</code> and <code>127</code></td></tr>
	<tr><td>Unsigned Byte</td>     <td>1</td>                   <td>Integer between <code>0</code> and <code>255</code></td></tr>
	<tr><td>Short</td>             <td>2</td>                   <td>Integer between <code>-32,768</code> and <code>32,767</code></td></tr>
	<tr><td>Unsigned Short</td>    <td>2</td>                   <td>Integer between <code>0</code> and <code>65,535</code></td></tr>
	<tr><td>VarInt</td>            <td>≥1, ≤10 </td>            <td>Integer between <code>0</code> and <code>18,446,744,073,709,551,615</code></td></tr>
	<tr><td>String</td>            <td>≥1, ≤65535</td>          <td>Big endian array of UTF8 characters up to <code>65,535</code> characters in length</td></tr>
	<tr><td>Byte Array</td>        <td>≥1, ≤65535</td>          <td>Big endian array of bytes up to <code>65,535</code> elements in length</td></tr>
	<tr><td>Array of <code>x</code></td> <td>Sum of all <code>x</code></td> <td> A collection of data types</td></tr>
</table>

#### About VarInts
More information about variable length integers can be found on [Wikipedia]( https://en.wikipedia.org/wiki/LEB128#Encode_unsigned_integer )
##### Encoding a VarInt
```
do {
  byte = low order 7 bits of value;
  value >>= 7;
  if (value != 0) /* more bytes to come */
    set high order bit of byte;
  emit byte;
} while (value != 0);
```

##### Decoding a VarInt
```
result = 0;
shift = 0;
while (true) {
  byte = next byte in input;
  result |= (low order 7 bits of byte) << shift;
  if (high order bit of byte == 0)
    break;
  shift += 7;
}
```

### Packet Format
| Field         | Type          | Notes                  |
| ------------- | ------------- | ---------------------- |
| Length        | VarInt        | Length of data         |
| Packet Type   | Unsigned Byte | Type of data contained |
| Data          | Byte Array    | Depends on packet type |

#### `0x00` Message
| Field   | Type   | Notes                |
| ------- | ------ | -------------------- |
| Message | String | UTF-8 encoded string |
  
#### `0x01` Roster
<table>
	<tr><th colspan="2">Field</th>                 <th colspan="2">Type</th>                  <th>Notes</th></tr>
	<tr><td colspan="2">Count</td>                 <td colspan="2">VarInt</td>                <td>Number of elements in array</td>
	<tr><td rowspan="2">Users</td> <td>Length</td> <td rowspan="2">Array</td> <td>VarInt</td> <td>Length of User ID</td></tr>
	<tr>                           <td>User ID</td>                           <td>String</td> <td>User specific identifier</td></tr>
</table>
  
#### `0x04` RSA Key
| Field           | Type      | Notes                             |
| --------------- | --------- | --------------------------------- |
| Modulus Length  | VarInt    | Length of the Modulus byte array  |
| Modulus         | ByteArray | RSA Modulus as a byte array       |
| Exponent Length | VarInt    | Length of the Exponent byte array |
| Modulus         | ByteArray | RSA Exponent as a byte array      |
  
#### `0x05` AES Key
| Field      | Type      | Notes                            |
| ---------- | --------- | -------------------------------- |
| Key Length | VarInt    | Length of the AES Key byte array |
| Key        | ByteArray | AES Key as a byte array          |
| IV Length  | VarInt    | Length of the AES IV byte array  |
| IV         | ByteArray | AES IV as a byte array           |
  
#### `0x08` RSA Encrypted
<table>
	<tr><th>Field</th> <th>Type</th> <th>Notes</th></tr>
	<tr><td>Mesa Packet</td> <td>Byte Array</td> <td>Packet encrypted with RSA</td>
</table>
  
  
#### `0x09` AES Encrypted
<table>
	<tr><th>Field</th> <th>Type</th> <th>Notes</th></tr>
	<tr><td>Mesa Packet</td> <td>Byte Array</td> <td>Packet encrypted with AES</td>
</table>
  
#### `0x0C` Redirect
##### Client -> Server
<table>
	<tr><th>Field</th> <th>Type</th> <th>Notes</th></tr>
	<tr><td>Length</td>      <td>VarInt</td>     <td>Length of destination User ID</td></tr>
	<tr><td>Dest User ID</td> <td>String</td>    <td>Destination User ID</td></tr> 
	<tr><td>Mesa Packet</td> <td>Byte Array</td> <td>Packet to be redirected</td>
</table>

##### Server -> Client
<table>
	<tr><th>Field</th> <th>Type</th> <th>Notes</th></tr>
	<tr><td>Length</td>      <td>VarInt</td>     <td>Length of source User ID</td></tr> 
	<tr><td>Src User ID</td> <td>String</td>     <td>Source User ID</td></tr> 
	<tr><td>Mesa Packet</td> <td>Byte Array</td> <td>Packet to be redirected</td>
</table>
  
#### `0x0D` Chain
<table>
	<tr><th colspan="2">Field</th>                 <th colspan="2">Type</th>                      <th>Notes</th></tr>
	<tr><td colspan="2">Count</td>                 <td colspan="2">VarInt</td>                    <td>Number of elements in array</td>
	<tr><td rowspan="2">Users</td> <td>Length</td> <td rowspan="2">Array</td> <td>VarInt</td>     <td>Length of Mesa Packet</td></tr>
	<tr>                           <td>Mesa Packet</td>                       <td>Byte Array</td> <td>Packet to be enclosed</td></tr>
</table>
  
#### `0x10` Audio Begin
  Currently Undefined
  
#### `0x11` Audio Data
  Currently Undefined
  
#### `0x12` Audio End
  Currently Undefined
  
  
  
