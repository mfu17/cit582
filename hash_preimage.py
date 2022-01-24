import hashlib
import os

def hash_preimage(target_string):
    if not all( [x in '01' for x in target_string ] ):
        print( "Input should be a string of bits" )
        return
    nonce = b'\x00'

    #print(target_string)
    len_target = len(target_string)

    nonce = os.urandom(64)
    nonce_hex = hashlib.sha256(nonce).hexdigest()
    nonce_hex_as_binary = bin(int(nonce_hex, 16))

    while nonce_hex_as_binary[-len_target:] != target_string:
        nonce = os.urandom(64)
        nonce_hex = hashlib.sha256(nonce).hexdigest()
        nonce_hex_as_binary = bin(int(nonce_hex, 16))  
    #print(nonce_hex_as_binary)
    
    return( nonce )

