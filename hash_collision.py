import hashlib
import os

def hash_collision(k):
    if not isinstance(k,int):
        print( "hash_collision expects an integer" )
        return( b'\x00',b'\x00' )
    if k <= 0:
        print( "Specify a positive number of bits" )
        return( b'\x00',b'\x00' )
   
    #Collision finding code goes here
    x = b'\x00'
    y = b'\x00'

    x = os.urandom(64)
    x_hex = hashlib.sha256(x).hexdigest()
    x_hex_as_binary = bin(int(x_hex, 16))
    target = x_hex_as_binary[-k:]
    print(target)
    
    y = os.urandom(64)
    y_hex = hashlib.sha256(x).hexdigest()
    y_hex_as_binary = bin(int(x_hex, 16))
    while y_hex_as_binary[-k:] != target:
        y = os.urandom(64)
        y_hex = hashlib.sha256(x).hexdigest()
        y_hex_as_binary = bin(int(x_hex, 16))       

    return( x, y )




