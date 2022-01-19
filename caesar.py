
def encrypt(key,plaintext):
    ciphertext=""
    #YOUR CODE HERE
    for l in plaintext:
        ciphertext += chr((ord(l) + key - 65) % 26 + 65)    
        
    return ciphertext

def decrypt(key,ciphertext):
    plaintext=""
    #YOUR CODE HERE
    plaintext = encrypt(26 - key, ciphertext)
    
    return plaintext
